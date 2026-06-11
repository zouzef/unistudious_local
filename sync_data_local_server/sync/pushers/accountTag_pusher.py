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
		url = f"{settings.api_base_url}/slc/update-account-subject/{accountTagId}"
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
		url = f"{settings.api_base_url}/slc/delete-account-subject/{accountTagId}"
		response = requests.post(url, headers, timeout=10)
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
		AccountTag = new_data.get('')
	except Exception as e:
		logger.exception("Error in push accountTagadd: %s", e)
		return False

def push_accountTagUpdate(db, settings, row):
	pass

def push_accountTagDelete(db, settings, row):
	pass
