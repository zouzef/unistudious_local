import logging
import sys
import os
import json
import requests
from core.auth import get_token

# from server_local_api.core.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


def _send_create_accountSubject_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-account-subject"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		print(response.json())
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
			account_subject_id = response_data.get('id')
			logger.info("AccountSubject created")
			return True, account_subject_id
		elif response.status_code == 400:
			logger.error("Api Error 400: %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None
	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in create accountLevel: %s", e)
		return False, None


def _send_update_accountSubject_api(settings, payload, accountSubjectId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-account-subject/{accountSubjectId}"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountSubject updated - %s", response_data)
				return True, response_data
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
		elif response.status_code == 400:
			logger.error("Api Error 400: %s", response.text)
			return False, None
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False, None
	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in _send_update_accountSubject: %s", e)
		return False, None


def _send_delete_accountSubject_api(settings, accountSubjectId):
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
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
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

		# ── Fetch all sub-subjects tied to this account_subject (local id) ──
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT name, account_level_id, account_section_id
			   FROM account_sub_subject
			   WHERE account_subject_id = %s""",
			(AccountSubjectIdLocal,)
		)
		sub_subjects = cursor.fetchall()
		cursor.close()

		# subSubjectName[i], subSubjectLevelId[i], subSubjectSectionId[i]
		# must land as parallel arrays under these exact keys, since the
		# Symfony endpoint zips them by index — same pattern as session's
		# extra_data_* arrays.
		subSubjectName = []
		subSubjectLevelId = []
		subSubjectSectionId = []

		for sub in sub_subjects:
			subSubjectId.append(sub.get('id_prod') or '')
			subSubjectName.append(sub.get('name') or '')
			subSubjectLevelId.append(sub.get('account_level_id') or '')
			subSubjectSectionId.append(sub.get('account_section_id') or '')

		# Build payload as a LIST OF TUPLES, not a dict — a dict can't hold
		# duplicate keys, and form-encoding needs each subSubject* array
		# sent as repeated "key[]" entries for PHP to parse them as arrays.
		payload = [
			("subjectId", accountSubject),
			("otherSubject", OtherSubject),
			("description", Description),
		]

		# Drop None values (requests will skip them anyway, but keeps it clean)
		payload = [(k, v) for k, v in payload if v is not None]

		# subSubjectName[]/subSubjectLevelId[]/subSubjectSectionId[] are
		# marked Required=Yes by the API, so always send them — empty
		# entries if there are no sub-subjects.
		if sub_subjects:
			for i in range(len(subSubjectName)):
				payload.append(("subSubjectName[]", subSubjectName[i]))
				payload.append(("subSubjectLevelId[]", subSubjectLevelId[i]))
				payload.append(("subSubjectSectionId[]", subSubjectSectionId[i]))
		else:
			payload.append(("subSubjectName[]", ""))
			payload.append(("subSubjectLevelId[]", ""))
			payload.append(("subSubjectSectionId[]", ""))

		status, AccountSubjectId = _send_create_accountSubject_api(settings, payload)

		if status and AccountSubjectId:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"""UPDATE account_subject set id_prod = %s WHERE id = %s""",
				(AccountSubjectId, AccountSubjectIdLocal)
			)
			db.connection.commit()
			cursor.close()
			logger.info("AccountSubject updated id_prod=%s for local id=%s", AccountSubjectId, AccountSubjectIdLocal)

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

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id, name, account_level_id, account_section_id, id_prod
			   FROM account_sub_subject
			   WHERE account_subject_id = %s AND enabled = 1""",
			(AccountSubjectLocalId,)
		)
		sub_subjects = cursor.fetchall()

		cursor.execute(
			"""SELECT id_prod FROM account_subject WHERE id = %s""",
			(AccountSubjectLocalId,)
		)
		result = cursor.fetchone()
		cursor.close()

		if not result or not result.get('id_prod'):
			logger.error("No id_prod found for account_subject local id=%s", AccountSubjectLocalId)
			return False
		id_prod = result['id_prod']

		payload = [
			("subjectId", SubjectConfig),
			("otherSubject", OtherConfig),
			("description", Description),
			("status", str(bool(status)).lower() if status is not None else None),
		]
		payload = [(k, v) for k, v in payload if v is not None]

		for sub in sub_subjects:
			payload.append(("subSubjectId[]", sub.get('id_prod') or ''))
			payload.append(("subSubjectName[]", sub.get('name') or ''))
			payload.append(("subSubjectLevelId[]", sub.get('account_level_id') or ''))
			payload.append(("subSubjectSectionId[]", sub.get('account_section_id') or ''))

		success, response_data = _send_update_accountSubject_api(settings, payload, id_prod)

		if success and response_data:
			# The endpoint returns touched sub-subjects in the SAME order it
			# received them (one entry per iteration of its input loop, whether
			# matched-existing or newly created) — so zip by index against the
			# local list we just sent, same order, same length.
			remote_sub_subjects = response_data.get('data', {}).get('subSubjects', [])

			if len(remote_sub_subjects) == len(sub_subjects):
				cursor = db.connection.cursor()
				for local_sub, remote_sub in zip(sub_subjects, remote_sub_subjects):
					remote_id = remote_sub.get('id')
					if remote_id and local_sub.get('id_prod') != remote_id:
						cursor.execute(
							"""UPDATE account_sub_subject SET id_prod = %s WHERE id = %s""",
							(remote_id, local_sub['id'])
						)
				db.connection.commit()
				cursor.close()
			else:
				logger.error(
					"Sub-subject count mismatch for account_subject local id=%s: sent %d, got %d back — skipping id_prod sync",
					AccountSubjectLocalId, len(sub_subjects), len(remote_sub_subjects)
				)

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
		status = _send_delete_accountSubject_api(settings, id_prod)
		return status
	except Exception as e:
		logger.exception("Error in push_accountSubjectDelete: %s", e)
		return False
