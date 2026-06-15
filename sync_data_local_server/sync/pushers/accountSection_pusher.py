import logging
import sys
import os
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Remote API calls
# ---------------------------------------------------------------------------

def _send_create_accountSection_api(settings,payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-account-section"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload ,headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False,None
			account_section_id = response_data.get('id')
			logger.info("AccountSection created ")
			return True,account_section_id

		elif response.status_code == 400:
			logger.error("Api Error 400: %s", response.text)
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

def _send_update_accountSection_api(settings,payload,accounSectionId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-account-section/{accounSectionId}"

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountSection updated — %s", response_data)
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

def _send_delete_accountSection_api(settings,accountSectionId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-account-section/{accountSectionId}"
		response = requests.post(url, headers=headers, timeout=10)
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


def push_accountSectionAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		AccountSection = new_data.get('section_config_id')
		OtherSection = new_data.get('other_section') or None
		Description = new_data.get('description') or None
		AccountSectionIdLocal = new_data.get('id')

		payload = {
			"sectionId":AccountSection,
			"otherSection":OtherSection or "",
			"description":Description or ""
		}
		status, AccountSectionId = _send_create_accountSection_api(settings,payload)
		if status and AccountSectionId:
			cursor_save = db.connection.cursor(dictionary=True)
			cursor_save.execute(
				"""UPDATE account_section set id_prod = %s WHERE id = %s""",
				(AccountSectionId,AccountSectionIdLocal)
			)
			db.connection.commit()
			cursor_save.close()
			logger.info("AccountSection updated <UNK> %s", AccountSectionIdLocal)

		return status

	except Exception as e:
		logger.exception("Error in push accountSectionAdd: %s", e)
		return False

def push_accountSectionUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		AccountSectionLocalId = new_data.get('id')
		SectionConfigId = new_data.get('section_config_id')
		OtherConfig = new_data.get('other_section') or None
		Description = new_data.get('description') or None
		Status = new_data.get('status')
		payload ={
			"sectionId":SectionConfigId,
			"otherSection":OtherConfig,
			"description":Description,
			"status":Status
		}
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM account_section WHERE id = %s""",
			(AccountSectionLocalId,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		success =_send_update_accountSection_api(settings,payload,id_prod)
		return success
	except Exception as e:
		logger.exception("Error in push_accountSectionUpdate: %s", e)
		return False

def push_accountSectionDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		accountSection = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM account_section WHERE id = %s""",
			(accountSection,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		status = _send_delete_accountSection_api(settings,id_prod)
		return status

	except Exception as e:
		logger.exception("Error in push_accountLevelUpdate: %s", e)
		return False