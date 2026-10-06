import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# => API Sync function
def _send_insert_Room_api(settings, payload, local_id):
	try:
		token = get_token()
		headers = {'Authorization': f'Bearer {token}'}
		url = f"{settings.api_base_url}/slc/create-room/{local_id}"
		response = requests.post(url, headers=headers, data=payload, timeout=10)

		if response.status_code in (200, 201):
			try:
				response_data = response.json()
			except ValueError:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None

			room_id_prod = (response_data.get('room') or {}).get('id')
			if not room_id_prod:
				logger.error("Room created remotely but no id in response: %s", response.text)
			return True, room_id_prod

		logger.error("Create room failed (%s): %s", response.status_code, response.text)
		return False, None

	except Exception as e:
		logger.exception("Remote API error in create room: %s", e)
		return False, None


def _send_update_Room_api(settings, payload, local_id, room_id):
	try:
		token = get_token()
		headers = {'Authorization': f'Bearer {token}'}
		url = f"{settings.api_base_url}/slc/update-room/{local_id}/{room_id}"
		response = requests.post(url, headers=headers, data=payload, timeout=10)

		if 200 <= response.status_code < 300:
			return True

		logger.error("Update room failed (%s): %s", response.status_code, response.text)
		return False

	except Exception as e:
		logger.exception("Remote API error in update room: %s", e)
		return False


def _send_delete_Room_api(settings, local_id, room_id):
	try:
		token = get_token()
		headers = {'Authorization': f'Bearer {token}'}
		url = f"{settings.api_base_url}/slc/delete-room/{local_id}/{room_id}"
		response = requests.post(url, headers=headers, timeout=10)

		if response.status_code == 200:
			return True

		# room already gone on the remote -> nothing left to do
		if response.status_code == 404:
			try:
				message = response.json().get('message', '')
			except ValueError:
				message = ''
			if message == "Room not found.":
				logger.warning("Delete room: room %s not found on remote, treating as deleted", room_id)
				return True

		logger.error("Delete room failed (%s): %s", response.status_code, response.text)
		return False

	except Exception as e:
		logger.exception("Remote API error in delete room: %s", e)
		return False


def push_room_Create(db, settings, row):
	cursor = None
	try:
		raw = row.get('new_data') or '{}'
		new_data = raw if isinstance(raw, dict) else json.loads(raw)

		name = new_data.get('name')
		capacity = new_data.get('capacity')
		local_id = new_data.get('local_id')
		room_id = new_data.get('id')

		if not local_id or not room_id:
			logger.error("push_room_Create: missing local_id or id in new_data: %s", new_data)
			return False

		payload = {
			"name": name,
			"capacity": capacity,
		}
		success, room_id_prod = _send_insert_Room_api(settings, payload, local_id)

		if success and room_id_prod:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE room SET id_prod = %s WHERE id = %s",
				(room_id_prod, room_id)
			)
			db.connection.commit()
			logger.info("Successfully updated Room ID: %s (id_prod=%s)", room_id, room_id_prod)

		return success

	except Exception as e:
		logger.exception("push_room_Create failed: %s", e)
		try:
			db.connection.rollback()
		except Exception:
			pass
		return False

	finally:
		if cursor:
			cursor.close()


def push_room_Update(db, settings, row):
	cursor = None
	try:
		raw = row.get('new_data') or '{}'
		new_data = raw if isinstance(raw, dict) else json.loads(raw)

		name = new_data.get('name')
		capacity = new_data.get('capacity')
		room_id = new_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"SELECT id_prod, local_id FROM room WHERE id = %s",
			(room_id,)
		)
		room = cursor.fetchone()
		if not room:
			logger.error("push_room_Update: room %s not found locally", room_id)
			return False

		room_id_prod = room.get('id_prod')
		if not room_id_prod:
			# room was never pushed to the remote yet -> retry next cycle
			logger.warning("push_room_Update: room %s has no id_prod yet, will retry", room_id)
			return False

		# audit rows created before local_id was added fall back to the DB value
		local_id = new_data.get('local_id') or room.get('local_id')
		if not local_id:
			logger.error("push_room_Update: no local_id for room %s", room_id)
			return False

		payload = {
			"name": name,
			"capacity": capacity,
		}
		return _send_update_Room_api(settings, payload, local_id, room_id_prod)

	except Exception as e:
		logger.exception("push_room_Update failed: %s", e)
		return False

	finally:
		if cursor:
			cursor.close()


def push_room_Delete(db, settings, row):
	cursor = None
	try:
		raw = row.get('new_data') or '{}'
		new_data = raw if isinstance(raw, dict) else json.loads(raw)

		room_id = new_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"SELECT id_prod, local_id FROM room WHERE id = %s",
			(room_id,)
		)
		room = cursor.fetchone()
		if not room:
			logger.error("push_room_Delete: room %s not found locally", room_id)
			return False

		room_id_prod = room.get('id_prod')
		if not room_id_prod:
			# never pushed to the remote: retry next cycle (the create push may still be pending)
			logger.warning("push_room_Delete: room %s has no id_prod yet, will retry", room_id)
			return False

		local_id = new_data.get('local_id') or room.get('local_id')
		if not local_id:
			logger.error("push_room_Delete: no local_id for room %s", room_id)
			return False

		return _send_delete_Room_api(settings, local_id, room_id_prod)

	except Exception as e:
		logger.exception("push_room_Delete failed: %s", e)
		return False

	finally:
		if cursor:
			cursor.close()
