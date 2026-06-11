import logging
import sys
import os
import json
import requests
from core.auth import get_token
# from server_local_api.core.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)



def _send_create_accountSubject_api(settings,payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-account-subject"

		logger.debug("POST %s | payload: %s", url,payload)

		response= requests.post(url,data=payload, headers=headers, timeout= 10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False,None
			account_subject_id = response_data.get('id')
			logger.info("AccountSubject created")
			return True,account_subject_id
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
		logger.exception("Remote API error in create accountLevel: %s", e)
		return False, None


def _send_update_accountSubject_api(settings,payload,accountSubjectId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-account-subject/{accountSubjectId}"

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountSubject updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_update_accountSubject: %s", e)
		return False

def _send_delete_accountSubject_api(settings,accountSubjectId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-account-subject/{accountSubjectId}"

		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccoutSubject deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s",response.status_code,response.text)
			return False

	except Exception as e:
		logger.exception("Remote API error in _send_update_accountSubject: %s", e)
		return False


def push_accountSubjectAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		accountSubject = new_data.get('subject_config_id')
		OtherSubject = new_data.get('other_subject') or None
		Description = new_data.get('description') or None
		AccountSubjectIdLocal = new_data.get('id')

		payload = {
			"subjectId":accountSubject,
			"otherSubject":OtherSubject,
			"description": Description
		}
		status,AccountSubjectId = _send_create_accountSubject_api(settings,payload)
		if status and AccountSubjectId:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"""UPDATE account_subject set id_prod = %s WHERE id = %s""",
				(AccountSubjectId,AccountSubjectIdLocal)
			)
			db.connection.commit()
			cursor.close()
			logger.info("AccountSubject updated <UNK> %s", AccountSubjectIdLocal)

		return status
	except Exception as e:
		logger.exception("Error in push accountSubjectAdd: %s", e)
		return False

def push_accountSubjectUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		AccountSubjectLocalId = new_data.get('id')
		SubjectConfig = new_data.get('subject_config_id')
		OtherConfig = new_data.get('other_subject') or None
		Description = new_data.get('description') or None
		status = new_data.get('status')
		payload = {
			"subjectId":SubjectConfig,
			"otherSubject":OtherConfig,
			"description":Description,
			"status":status
		}
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM account_subject WHERE id = %s""",
			(AccountSubjectLocalId,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		success = _send_update_accountSubject_api(settings,payload,id_prod)
		return success
	except Exception as e:
		logger.exception("Error in push_accountSubjectUpdate: %s", e)
		return False

def push_accountSubjectDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		accountSubject = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM account_subject WHERE id = %s""",
			(accountSubject,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		status = _send_delete_accountSubject_api(settings,id_prod)
		return status
	except Exception as e:
		logger.exception("Error in push_accountSubjectDelete: %s", e)
		return False