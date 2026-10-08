import logging
import os
import sys
import json
import requests
from core.auth import get_token
from utils.helpers import _map_ids_to_prod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

# Remote understood the request and refused the data -> undo the local action, no retry
# (403 is NOT here: it is a permission problem, not bad data, so we keep the local data and retry)
REJECT_CODES = {400, 404, 409, 422}


def _rejected(response):
	"""Returned instead of None when the remote refuses the data."""
	return {
		"rejected": True,
		"status_code": response.status_code,
		"reason": response.text,
	}


# ─────────────────────────────────────────────
# Local rollback
# ─────────────────────────────────────────────

def _rollback_local_camera(db, local_id):
	"""Delete the local camera that the remote refused.
	Only deletes when id_prod IS NULL, so an already-synced camera is never removed."""
	cursor = None
	try:
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute("SELECT id_prod FROM camera WHERE id = %s", (local_id,))
		row = cursor.fetchone()
		if not row:
			logger.warning("Rollback: local camera id=%s already gone", local_id)
			return True
		if row.get("id_prod"):
			logger.error("Rollback skipped: camera id=%s already has id_prod=%s", local_id, row["id_prod"])
			return False

		cursor.execute("DELETE FROM camera WHERE id = %s AND id_prod IS NULL", (local_id,))
		db.connection.commit()

		logger.warning("🗑️ Local camera id=%s deleted: remote rejected it", local_id)
		return True
	except Exception as e:
		db.connection.rollback()
		logger.exception("Rollback failed for local camera id=%s: %s", local_id, e)
		return False
	finally:
		if cursor:
			cursor.close()


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

def _send_create_camera_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-camera"
		logger.debug("POST %s | payload: %s", url, payload)
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
			camera_id = response_data.get('data', {}).get('id')
			return True, camera_id
		elif response.status_code in REJECT_CODES:
			logger.error("Create camera REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		elif response.status_code == 403:
			logger.error("Create camera FORBIDDEN (token needs ROLE_SLC): %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None
	except Exception as e:
		logger.exception("Remote API error in create camera: %s", e)
		return False, None


def _send_update_camera_api(settings, payload, cameraId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-camera/{cameraId}"
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Slc_camera updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in update camera: %s", e)
		return False


def _send_delete_camera_api(settings, cameraId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-camera/{cameraId}"
		response = requests.post(url, headers=headers, verify=False, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Camera deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		elif response.status_code == 404:
			# Already gone on remote -> remote already matches local
			logger.warning("Delete camera %s: already gone on remote (%s)", cameraId, response.text)
			return True
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_camera: %s", e)
		return False


# ─────────────────────────────────────────────
# Push functions (called by pusher dispatcher)
# ─────────────────────────────────────────────

def _resolve_remote_room(db, local_room_id, label, local_id):
	"""Returns (ok, remote_room_id). ok=False means the room is not synced yet -> retry later."""
	if not local_room_id:
		return True, None
	local_room_id = int(local_room_id)
	room_map = _map_ids_to_prod(db, "room", "id", [local_room_id])
	remote_room_id = room_map.get(local_room_id)
	if not remote_room_id:
		logger.warning(
			"%s local=%s: room local=%s not synced yet (no id_prod), retry later",
			label, local_id, local_room_id
		)
		return False, None
	return True, remote_room_id


def push_cameraAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_id = new_data.get('id')

		# The remote knows rooms by their remote id (id_prod), not the local id
		ok_room, remote_room_id = _resolve_remote_room(db, new_data.get("room_id"), "Camera", local_id)
		if not ok_room:
			return False

		payload = {
			"name": new_data.get('name'),
			"mac": new_data.get("mac_id"),
			"status": new_data.get("active"),
			"roomId": remote_room_id,
			"username": new_data.get("username"),
			"password": new_data.get("password"),
			"type": new_data.get("type"),
		}

		status, result = _send_create_camera_api(settings, payload)

		if not status:
			# Remote refused the data -> undo the local action
			if isinstance(result, dict) and result.get("rejected"):
				logger.error(
					"Remote rejected camera local=%s [%s]: %s",
					local_id, result.get("status_code"), result.get("reason")
				)
				_rollback_local_camera(db, local_id)
				return True  # handled: the audit row must not be retried
			return False  # network / 403 / 5xx: retry later

		camera_id = result
		if camera_id:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE camera SET id_prod = %s WHERE id = %s",
				(camera_id, local_id)
			)
			db.connection.commit()
			cursor.close()
			logger.info("✅ Camera synced: local=%s remote=%s", local_id, camera_id)
		else:
			logger.error("Camera local=%s created on remote but no id returned", local_id)

		return status
	except Exception as e:
		logger.exception("Error in push Camera : %s", e)
		return False


def push_cameraUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_id = new_data.get('id')

		ok_room, remote_room_id = _resolve_remote_room(db, new_data.get("room_id"), "Camera update", local_id)
		if not ok_room:
			return False

		payload = {
			"name": new_data.get('name'),
			"mac": new_data.get("mac_id"),
			"status": new_data.get("active"),
			"roomId": remote_room_id,
			"username": new_data.get("username"),
			"password": new_data.get("password"),
			"type": new_data.get("type"),
		}

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM camera WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("Camera not found locally for id %s", local_id)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			logger.error("Camera local=%s has no id_prod yet, skipping update", local_id)
			return False

		return _send_update_camera_api(settings, payload, id_prod)
	except Exception as e:
		logger.exception("Error in push_CameraUpdate: %s", e)
		return False


def push_cameraDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		local_id = old_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM camera WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("Camera not found locally for id %s", local_id)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			# Never reached the remote (or its create was rolled back): nothing to delete there
			logger.warning("Camera local=%s has no id_prod, nothing to delete on remote", local_id)
			return True

		return _send_delete_camera_api(settings, id_prod)
	except Exception as e:
		logger.exception("Error in push_cameraDelete: %s", e)
		return False