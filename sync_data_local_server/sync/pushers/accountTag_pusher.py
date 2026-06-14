import logging
import sys
import os
import json
import requests
from core.auth import get_token
# from server_local_api.core.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ------------------------------------------------
# Remote API calls
# ------------------------------------------------


def _send_create_accountTag_api(settings,payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-account-tag"

		logger.debug(" POST %s | payload: %s", url, payload)

		response = requests.post(url, data = payload, headers= headers, timeout= 10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None

			accountTagId = response_data.get('id')
			logger.info("AccountTag created ")
			return True, accountTagId
		elif response.status_code == 400:
			logger.error("Api Error 400: %s", response.text)
			return False,None

		else:
			logger.error("Unexpected status %s: %s", response.status_code,response.text)
			return False,None

	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in create accountTag: %s", e)
		return False, None

def _send_update_accountTag_api(settings, payload, accountTagId):
	try:
		token = get_token()
		headers= {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-account-tag/{accountTagId}"
		response = requests.post(url, data =payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountTag updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False

	except Exception as e:
		logger.exception("Remote API error in _send_update_calander: %s", e)
		return False

def _send_delete_accountTag_api(settings, accountTagId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-account-tag/{accountTagId}"
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountTag deleted - %s", response_data)
				return True

			except Exception as e:
				logger.error("Invalid JSON response: %s",response.text)
				return False

	except Exception as e:
		logger.exception ("Remote API error in _send_delete_accountTag_api: %s", e)
		return False


def push_accountTagAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		TagConfig = new_data.get('tag_config_id')
		OtherTag = new_data.get('other_tag')  or None
		Description = new_data.get('description')  or None
		Status = new_data.get('status')
		Public = new_data.get('status')
		AccountTagIdLocal = new_data.get('id')
		payload = {
			"tagId":TagConfig,
			"otherTag": OtherTag,
			"description": Description,
			"status": Status,
			"public": Public
		}
		status,AccountTagId = _send_create_accountTag_api(settings,payload)
		if status and AccountTagId:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"""UPDATE account_tag set id_prod = %s WHERE id = %s""",
				(AccountTagId, AccountTagIdLocal)
			)
			db.connection.commit()
			cursor.close()
			logger.info("AccountTag updated <UNK>  %s", AccountTagIdLocal)

		return status
	except Exception as e:
		logger.exception("Error in push accountTagadd: %s", e)
		return False

def push_accountTagUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		TagConfig = new_data.get('tag_config_id') or None
		OtherTag = new_data.get('other_tag') or None
		Public = new_data.get('public')
		Description = new_data.get('description')
		AccountTagIdLocal = new_data.get('id')
		payload = {
			"tagId": TagConfig,
			"otherTag": OtherTag,
			"description": Description,
			"public": Public
		}
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM account_tag WHERE id = %s """,
			(AccountTagIdLocal,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		success = _send_update_accountTag_api(settings, payload, id_prod)
		return success

	except Exception as e:
		logger.exception("Error in push_accountTag Update: %s", e)
		return False

def push_accountTagDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		AccountTagIdLocal = old_data.get('id')
		cursor = db.connection.cursor(dictionary = True)
		cursor.execute(
			"""SELECT id_prod FROM account_tag WHERE id = %s""",
			(AccountTagIdLocal,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		status =  _send_delete_accountTag_api(settings,id_prod)
		return status
	except Excpetion as e:
		logger.exception("Error in push_accountTagDelete: %s", e)
		return False

