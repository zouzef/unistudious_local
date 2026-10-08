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

def _rollback_local_door(db, local_id):
	"""Delete the local door that the remote refused.
	Only deletes when id_prod IS NULL, so an already-synced door is never removed."""
	cursor = None
	try:
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute("SELECT id_prod FROM slc_door WHERE id = %s", (local_id,))
		row = cursor.fetchone()
		if not row:
			logger.warning("Rollback: local door id=%s already gone", local_id)
			return True
		if row.get("id_prod"):
			logger.error("Rollback skipped: door id=%s already has id_prod=%s", local_id, row["id_prod"])
			return False

		cursor.execute("DELETE FROM slc_door WHERE id = %s AND id_prod IS NULL", (local_id,))
		db.connection.commit()

		logger.warning("🗑️ Local door id=%s deleted: remote rejected it", local_id)
		return True
	except Exception as e:
		db.connection.rollback()
		logger.exception("Rollback failed for local door id=%s: %s", local_id, e)
		return False
	finally:
		if cursor:
			cursor.close()


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

def _send_create_door_api(settings, payload):
	url = f"{settings.api_base_url}/slc/create-door"
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
			door_id = response_data.get('data', {}).get('id')
			logger.info("Door created")
			return True, door_id
		elif response.status_code in REJECT_CODES:
			logger.error("Create door REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		elif response.status_code == 403:
			logger.error("Create door FORBIDDEN (token needs ROLE_SLC): %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None
	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in create door: %s", e)
		return False, None


def _send_update_door_api(settings, payload, doorId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-door/{doorId}"
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("SlcDoor updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		elif response.status_code == 403:
			logger.error("Update door FORBIDDEN: %s", response.text)
			return False
		elif response.status_code == 404:
			logger.error("Update door: door %s not found on remote: %s", doorId, response.text)
			return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_update_door_api: %s", e)
		return False


def _send_delete_door_api(settings, doorId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-door/{doorId}"

		response = requests.post(url, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Door deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		elif response.status_code == 404:
			# Already gone on remote -> remote already matches local
			logger.warning("Delete door %s: already gone on remote (%s)", doorId, response.text)
			return True
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_door: %s", e)
		return False


# ─────────────────────────────────────────────
# Push functions (called by pusher dispatcher)
# ─────────────────────────────────────────────

def push_doorAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_id = new_data.get('id')
		name = new_data.get('name')
		local_room_id = new_data.get('room_id')
		mac_id = new_data.get('mac_id')
		password = new_data.get('password')

		# The remote knows rooms by their remote id (id_prod), not the local id
		remote_room_id = None
		if local_room_id:
			local_room_id = int(local_room_id)
			room_map = _map_ids_to_prod(db, "room", "id", [local_room_id])
			remote_room_id = room_map.get(local_room_id)
			if not remote_room_id:
				logger.warning(
					"Door local=%s: room local=%s not synced yet (no id_prod), retry later",
					local_id, local_room_id
				)
				return False

		payload = {
			"name": name,
			"mac": mac_id,
			"roomId": remote_room_id,
			"password": password,
		}

		ok, result = _send_create_door_api(settings, payload)

		if not ok:
			# Remote refused the data -> undo the local action
			if isinstance(result, dict) and result.get("rejected"):
				logger.error(
					"Remote rejected door local=%s [%s]: %s",
					local_id, result.get("status_code"), result.get("reason")
				)
				_rollback_local_door(db, local_id)
				return True  # handled: the audit row must not be retried
			return False  # network / 403 / 5xx: retry later

		door_id_prod = result
		if door_id_prod:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE slc_door SET id_prod = %s WHERE id = %s",
				(door_id_prod, local_id)
			)
			db.connection.commit()
			cursor.close()
			logger.info("✅ Door synced: local=%s remote=%s", local_id, door_id_prod)
		else:
			logger.error("Door local=%s created on remote but no id returned", local_id)

		return ok
	except Exception as e:
		logger.exception("Error in push DoorAdd: %s", e)
		return False


def push_doorUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_id = new_data.get('id')
		name = new_data.get('name')
		mac = new_data.get('mac_id')
		local_room_id = new_data.get('room_id')
		password = new_data.get('password')
		status = new_data.get('status')

		remote_room_id = None
		if local_room_id:
			local_room_id = int(local_room_id)
			room_map = _map_ids_to_prod(db, "room", "id", [local_room_id])
			remote_room_id = room_map.get(local_room_id)
			if not remote_room_id:
				logger.warning(
					"Door update local=%s: room local=%s not synced yet, retry later",
					local_id, local_room_id
				)
				return False

		payload = {
			"name": name,
			"mac": mac,
			"roomId": remote_room_id,
			"password": password,
			"status": status,
		}

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM slc_door WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("Door not found locally for id %s", local_id)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			logger.error("Door local=%s has no id_prod yet, skipping update", local_id)
			return False

		return _send_update_door_api(settings, payload, id_prod)
	except Exception as e:
		logger.exception("Error in push_DoorUpdate: %s", e)
		return False


def push_doorDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		local_id = old_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM slc_door WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("Door not found locally for id %s", local_id)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			# Never reached the remote (or its create was rolled back): nothing to delete there
			logger.warning("Door local=%s has no id_prod, nothing to delete on remote", local_id)
			return True

		return _send_delete_door_api(settings, id_prod)
	except Exception as e:
		logger.exception("Error in push_doorDelete: %s", e)
		return False