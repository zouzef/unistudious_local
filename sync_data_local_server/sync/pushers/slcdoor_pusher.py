import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


def _send_create_door_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-door"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False,None
			doorId = response_data.get('data', {}).get('id')
			logger.info("Door created")
			return True, doorId
		elif response.status_code == 400:
			logger.error("Invalid JSON response: %s", response.text)
			return False,None
		else:

			logger.error("Unexpected status %s: %s", response.status_code,response.text)
			return False, None
	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in create CompletionTag: %s", e)
		return False, None

def _send_update_door_api(settings, payload, doorId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-door/{doorId}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("SlcDoor updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
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

		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Door deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_door: %s", e)
		return False


def push_doorAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		id = new_data.get('id')
		name = new_data.get('name')
		slc_id = new_data.get('slc_id')
		room_id = new_data.get('room_id')
		mac_id = new_data.get('mac_id')
		password = new_data.get('password')
		status = new_data.get('status')
		created_at = new_data.get('created_at')
		oc = new_data.get('oc')


		payload = {
			"name": name,
			"mac": mac_id,
			"roomId": room_id,
			"password": password
		}
		status, doorIdProd = _send_create_door_api(settings, payload)
		if status and doorIdProd:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				""" UPDATE slc_door set id_prod = %s WHERE id = %s""",
				(doorIdProd, id)
			)
			db.connection.commit()
			cursor.close()
			logger.info("slcDoor updated <UNK> %s", id)

		return status
	except Exception as e:
		logger.exception("Error in push DoorAdd: %s", e)
		return False

def push_doorUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		doorId = new_data.get('id')
		name = new_data.get('name')
		mac = new_data.get('mac_id')
		roomId = new_data.get('room_id')
		password = new_data.get('password')
		status = new_data.get('status')
		payload ={
			"name": name,
			"mac": mac,
			"roomId": roomId,
			"password": password,
			"status": status
		}
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("""
			SELECT id_prod FROM slc_door WHERE id = %s
		""",(doorId,))
		result = cursor.fetchone()
		id_prod = result['id_prod']
		success = _send_update_door_api(settings, payload, id_prod)
		return success
	except Exception as e:
		logger.exception("Error in push_DoorUpdate: %s", e)
		return False

def push_doorDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		doorId = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM slc_door WHERE id = %s""",
			(doorId,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		status = _send_delete_door_api(settings, id_prod)
		return status
	except Exception as e:
		logger.exception("Error in push_doorDelete: %s", e)
		return False