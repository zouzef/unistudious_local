import sys
import os
import json
import logging
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Remote API calls
# ---------------------------------------------------------------------------

def _send_create_accountLevel_api(settings,payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-account-level"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload ,headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False,None,
			account_level_id = response_data.get('id')
			logger.info("AccountLevel created ")
			return True,account_level_id

		elif response.status_code == 400:
			logger.error("Api Error 400: %S", response.text)
			return False,None

		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False,None

	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None

	except Exception as e:
		logger.exception("Remote API error in create accountLevel: %s", e)
		return False, None

def _send_update_accountLevel_api(settings,payload,accounLevelId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-account-level/{accounLevelId}"

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountLevel updated — %s", response_data)
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

def _send_delete_accountLevel_api(settings,payload,accountLevelId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-account-level/{accountLevelId}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountLevel deleted - %s",response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text )
			return False

	except Exception as e:
		logger.exception("Rempte API error in _send_delete_accountLevel_api: %s",e)
		return False


def push_accountLevelAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		AccountLevelId = new_data.get('id')
	except Exception as e:
		logger.exception("Error in push_accountLevelAdd: %s", e)
		return False
