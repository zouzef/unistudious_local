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

def _rollback_local_tablet(db, local_id):
	"""Delete the local tablet that the remote refused.
	Only deletes when id_prod IS NULL, so an already-synced tablet is never removed."""
	cursor = None
	try:
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute("SELECT id_prod FROM tablet WHERE id = %s", (local_id,))
		row = cursor.fetchone()
		if not row:
			logger.warning("Rollback: local tablet id=%s already gone", local_id)
			return True
		if row.get("id_prod"):
			logger.error("Rollback skipped: tablet id=%s already has id_prod=%s", local_id, row["id_prod"])
			return False

		cursor.execute("DELETE FROM tablet WHERE id = %s AND id_prod IS NULL", (local_id,))
		db.connection.commit()

		logger.warning("🗑️ Local tablet id=%s deleted: remote rejected it", local_id)
		return True
	except Exception as e:
		db.connection.rollback()
		logger.exception("Rollback failed for local tablet id=%s: %s", local_id, e)
		return False
	finally:
		if cursor:
			cursor.close()


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

def _send_create_tablet_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-tablet"
		logger.debug("POST %s | payload: %s", url, payload)
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
			tablet_id = response_data.get('data', {}).get('id')
			return True, tablet_id
		elif response.status_code in REJECT_CODES:
			# 400: name/mac missing | 404: room not found or not in your local
			logger.error("Create tablet REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		elif response.status_code == 403:
			logger.error("Create tablet FORBIDDEN (token needs ROLE_SLC): %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None
	except Exception as e:
		logger.exception("Remote API error in create tablet: %s", e)
		return False, None


def _send_update_tablet_api(settings, payload, tabletId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-tablet/{tabletId}"
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Slc_tablet updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		elif response.status_code == 403:
			logger.error("Update tablet FORBIDDEN: %s", response.text)
			return False
		elif response.status_code == 404:
			logger.error("Update tablet: tablet %s not found or disabled on remote: %s", tabletId, response.text)
			return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in update tablet: %s", e)
		return False


def _send_delete_tablet_api(settings, tabletId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-tablet/{tabletId}"
		response = requests.post(url, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Tablet deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		elif response.status_code == 404:
			# Already disabled / does not exist on remote -> remote already matches local
			logger.warning("Delete tablet %s: already gone on remote (%s)", tabletId, response.text)
			return True
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_tablet: %s", e)
		return False


# ─────────────────────────────────────────────
# Push functions (called by pusher dispatcher)
# ─────────────────────────────────────────────

def push_tabletAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		idLocal = new_data.get('id')
		name = new_data.get('name')
		mac = new_data.get("mac_id")
		statuss = new_data.get("active")
		local_room_id = new_data.get("room_id")
		password = new_data.get("password")

		# The remote knows rooms by their remote id (id_prod), not the local id
		remote_room_id = None
		if local_room_id:
			local_room_id = int(local_room_id)
			room_map = _map_ids_to_prod(db, "room", "id", [local_room_id])
			remote_room_id = room_map.get(local_room_id)
			if not remote_room_id:
				logger.warning(
					"Tablet local=%s: room local=%s not synced yet (no id_prod), retry later",
					idLocal, local_room_id
				)
				return False

		payload = {
			"name": name,
			"mac": mac,
			"roomId": remote_room_id,
			"status": statuss,
			"password": password,
		}

		status, result = _send_create_tablet_api(settings, payload)

		if not status:
			# Remote refused the data -> undo the local action
			if isinstance(result, dict) and result.get("rejected"):
				logger.error(
					"Remote rejected tablet local=%s [%s]: %s",
					idLocal, result.get("status_code"), result.get("reason")
				)
				_rollback_local_tablet(db, idLocal)
				return True  # handled: the audit row must not be retried
			return False  # network / 403 / 5xx: retry later

		tablet_id = result
		if tablet_id:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE tablet SET id_prod = %s WHERE id = %s",
				(tablet_id, idLocal)
			)
			db.connection.commit()
			cursor.close()
			logger.info("✅ Tablet synced: local=%s remote=%s", idLocal, tablet_id)
		else:
			logger.error("Tablet local=%s created on remote but no id returned", idLocal)

		return status
	except Exception as e:
		logger.exception("Error in push Tablet : %s", e)
		return False


def push_tabletUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		idLocal = new_data.get('id')
		name = new_data.get('name')
		mac = new_data.get("mac_id")
		statuss = new_data.get("active")
		local_room_id = new_data.get("room_id")
		password = new_data.get("password")

		remote_room_id = None
		if local_room_id:
			local_room_id = int(local_room_id)
			room_map = _map_ids_to_prod(db, "room", "id", [local_room_id])
			remote_room_id = room_map.get(local_room_id)
			if not remote_room_id:
				logger.warning(
					"Tablet update local=%s: room local=%s not synced yet, retry later",
					idLocal, local_room_id
				)
				return False

		payload = {
			"name": name,
			"mac": mac,
			"roomId": remote_room_id,
			"status": statuss,
			"password": password,
		}

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM tablet WHERE id = %s", (idLocal,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("Tablet not found locally for id %s", idLocal)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			logger.error("Tablet local=%s has no id_prod yet, skipping update", idLocal)
			return False

		return _send_update_tablet_api(settings, payload, id_prod)
	except Exception as e:
		logger.exception("Error in push_TabletUpdate: %s", e)
		return False


def push_tabletDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		localId = old_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM tablet WHERE id = %s", (localId,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("Tablet not found locally for id %s", localId)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			# Never reached the remote (or its create was rolled back): nothing to delete there
			logger.warning("Tablet local=%s has no id_prod, nothing to delete on remote", localId)
			return True

		return _send_delete_tablet_api(settings, id_prod)
	except Exception as e:
		logger.exception("Error in delete_tablet: %s", e)
		return False