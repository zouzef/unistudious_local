import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

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
				return False,None
			tabletID = response_data.get('data', {}).get('id')
			return True, tabletID
		elif response.status_code == 400:
			logger.error("Invalid JSON response: %s", response.text)
			return False,None
		else:
			logger.error("Unexpected status %s: %s", response.status_code,response.text)
			return False, None
	except Exception as e:
		logger.exception("Remote API error in create tablet: %s", e)
		return False,None

def _send_update_tablet_api(settings,payload,tabletId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-tablet/{tabletId}"
		response = requests.post(url, data=payload, headers=headers,timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Slc_tablet updated - %s", response_data)
				return True
			except Exception :
				logger.error("Invalid JSON response: %s", response.text)
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
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Tablet deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_tablet: %s", e)
		return False


def push_tabletAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		idLocal = new_data.get('id')
		name = new_data.get('name')
		mac = new_data.get("mac_id")
		statuss = new_data.get("active")
		roomId = new_data.get("room_id")
		password = new_data.get("password")

		payload = {
			"name": name,
			"mac": mac,
			"roomId": roomId,
			"status": statuss,
			"password": password,
		}
		status, tablet_id = _send_create_tablet_api(settings, payload)
		if status and tablet_id:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute("""
				UPDATE tablet set id_prod = %s WHERE id = %s
			""", (tablet_id, idLocal))
			db.connection.commit()
			cursor.close()
			logger.info("Tablet updated <UNK> %s", idLocal)

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
		roomId = new_data.get("room_id")
		password = new_data.get("password")

		payload = {
			"name": name,
			"mac": mac,
			"roomId": roomId,
			"status": statuss,
			"password": password,
		}

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("""
			SELECT id_prod FROM tablet WHERE id = %s
		""",(idLocal,))
		result = cursor.fetchone()
		cursor.close()
		if not result:
			logger.error("Tablet not found locally for id %s", idLocal)
			return False
		id_prod = result['id_prod']
		success = _send_update_tablet_api(settings, payload, id_prod)
		return success
	except Exception as e:
		logger.exception("Error in push_TabletUpdate: %s", e)
		return False

def push_tabletDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data','{}'))
		localId = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM tablet WHERE id = %s""",(localId,)
		)
		result = cursor.fetchone()
		cursor.close()
		if not result:
			logger.error("Tablet not found locally for id %s", localId)
			return False
		id_prod = result['id_prod']
		status = _send_delete_tablet_api(settings,id_prod)
		return status
	except Exception as e:
		logger.exception("Error in delete_tablet: %s", e)
		return False