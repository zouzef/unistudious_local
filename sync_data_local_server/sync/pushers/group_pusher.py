import logging
import os
import sys
import json

import requests
from core.auth import get_token
from utils.helpers import _find_key_by_prefix

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ==============================================
# GROUP API
# ==============================================
def _send_create_group_api(settings, payload, data_group):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}

		sessionId = data_group.get('session_id')
		localId = data_group.get('local_id')
		url = f"{settings.api_base_url}/slc/create-group/{sessionId}/{localId}"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None

			groupIdProd = response_data.get('groupId')  # was response.get (bug)
			logger.info("Group Created")
			return True, groupIdProd
		elif response.status_code == 400:
			logger.error("Invalid JSON response: %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response)
			return False, None

	except requests.exceptions.Timeout:
		logger.error("Request timeout(10s) — %s", url)
		return False, None

	except Exception as e:
		logger.exception("Remote API error in create CompletionTag: %s", e)
		return False, None

def _send_update_group_api(settings, payload, group_id, session_id, local_id):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}

		url = f"{settings.api_base_url}/slc/edit-group/{group_id}/{session_id}/{local_id}"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, json=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None

			logger.info("Group %s updated remotely", group_id)
			return True, response_data
		elif response.status_code == 400:
			logger.error("Invalid JSON response: %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None

	except requests.exceptions.Timeout:
		logger.error("Request timeout(10s) — %s", url)
		return False, None

	except Exception as e:
		logger.exception("Remote API error in _send_update_group_api: %s", e)
		return False, None

def _send_delete_group_api(settings, groupId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/scl/delete-group"
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Door deleted - %s", response_data)
				return True

			except Exception:
				logger.error("Invalid JSON response: %s",response.text)
				return False
		else:
			logger.error("Remote API return")

	except Exception as e:
		logger.exception("Remote API error in _send_delete_group: %s",e)
		return False




def push_groupAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		id = new_data.get('id')
		session_id = new_data.get('session_id')
		local_id = new_data.get('local_id')
		name = new_data.get('name')
		capacity = new_data.get('capacity')

		relations = new_data.get('relations')

		if not relations:
			legacy_subject_id = new_data.get('subject_id')
			legacy_teacher_id = new_data.get('teacher_id')
			if legacy_subject_id and legacy_teacher_id:
				relations = [{
					"subject_id": legacy_subject_id,
					"teacher_id": legacy_teacher_id
				}]
			else:
				relations = []

		if not relations:
			logger.warning("push_groupAdd: no subject/teacher relations for group id %s, skipping", id)
			return False, None

		# Remote API wants parallel arrays, index-aligned (teacherId[i] <-> subjectId[i])
		teacher_ids = [r.get('teacher_id') for r in relations]
		subject_ids = [r.get('subject_id') for r in relations]

		# Build the dynamic index suffix: 1-based, comma-separated -> "1,2,3"
		index_list = ",".join(str(i + 1) for i in range(len(relations)))

		payload = {
			"name": name,
			"capacity": capacity,
			f"teacherId[{index_list}]": teacher_ids,
			f"subjectId[{index_list}]": subject_ids
		}
		print(payload)
		status, groupIdProd = _send_create_group_api(settings, payload, new_data)

		if status and groupIdProd:  # was "doorIdProd" (undefined var bug)
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"""UPDATE relation_group_local_session SET id_prod = %s WHERE id = %s""",
				(groupIdProd, id)  # was (id, groupIdProd) — swapped (bug)
			)
			db.connection.commit()
			cursor.close()
			logger.info("Group updated, local id %s -> prod id %s", id, groupIdProd)

		return status, groupIdProd

	except Exception as e:
		logger.exception("Error in push GroupAdd: %s", e)
		return False, None

def push_groupUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))

		group_id = new_data.get('id') or row.get('record_id')

		# id_prod is what the remote API needs, not the local id
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"SELECT id_prod, session_id, local_id FROM relation_group_local_session WHERE id = %s",
			(group_id,)
		)
		group_row = cursor.fetchone()
		cursor.close()

		if not group_row or not group_row.get('id_prod'):
			logger.warning("push_groupUpdate: no id_prod found for local group id %s, skipping", group_id)
			return False, None

		group_id_prod = group_row['id_prod']
		session_localId = group_row['session_id']
		local_localId = group_row['local_id']

		# Resolve session's prod id using the same db connection
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"SELECT id_prod FROM session WHERE id = %s",
			(session_localId,)
		)
		session_row = cursor.fetchone()
		cursor.close()

		if not session_row or not session_row.get('id_prod'):
			logger.warning("push_groupUpdate: no id_prod found for session id %s, skipping", session_localId)
			return False, None

		session_prodId = session_row['id_prod']

		delete_relation_ids = _find_key_by_prefix(new_data, "deleteRelationIds")
		update_relations = _find_key_by_prefix(new_data, "updateRelations")
		new_teacher_ids = _find_key_by_prefix(new_data, "newRelationTeacherId")
		new_subject_ids = _find_key_by_prefix(new_data, "newRelationSubjectId")

		payload = {
			"name": new_data.get('name'),
			"capacity": new_data.get('capacity'),
			"deleteRelationIds": delete_relation_ids,
			"updateRelations": update_relations,
			"newRelationTeacherId": new_teacher_ids,
			"newRelationSubjectId": new_subject_ids
		}

		print(payload)
		status, response_data = _send_update_group_api(settings, payload, group_id_prod, session_prodId, local_localId)

		if status:
			logger.info("Group updated remotely, local id %s -> prod id %s", group_id, group_id_prod)

		return status, response_data

	except Exception as e:
		logger.exception("Error in push_groupUpdate: %s", e)
		return False, None

def push_groupDelete():
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		groupId = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM relation_group_local_session WHERE id = %s""",
			(groupId,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		status = _send_delete_group_api(settings, id_prod)
		return status
	except Exception as e:
		logger.exception("Error in push_groupDelete: %s", e)
		return False


# ==============================================
# STUDENT GROUP API
# ==============================================

def _send_affect_user_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearze {token}"}
		url = f"{settings.api_base_url}/scl/affect-user"
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Affected user - %s", response.text)
				return False
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_affect_user_api %s", e)
		return False


	except Exception as e:
		logger.error("Invalid JSON response: %s", response.text)
		return False


def _send_disaffect_user_api():
	try:
		token = get_token()
		headers = {"Authorization": f"Beareer {token}"}
		url = f"{settings.api_base_url}/slc/disaffect-user"

		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Door deleted -%s", response.text)
				return True

			except Exception as e:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_disaffect_user: %s", e)
		return False




def push_affect_user():
	pass

def push_disaffect_user():
	pass
