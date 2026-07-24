import logging
import os
import sys
import json

import requests
from core.auth import get_token
from utils.helpers import _find_key_by_prefix, _map_ids_to_prod, _map_subject_ids_to_prod, _flatten_group_payload_to_form

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

		form_data = _flatten_group_payload_to_form(payload)
		logger.debug("POST %s | form_data: %s", url, form_data)
		response = requests.post(url, data=form_data, headers=headers, timeout=10)

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

def _send_delete_group_api(settings, data):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-group/{data.get('group_id')}/{data.get('sessionId')}/{data.get('localId')}"
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
		group_id = new_data.get('id')

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

		delete_relation_ids = _find_key_by_prefix(new_data, "deleteRelationIds") or []
		update_relations = _find_key_by_prefix(new_data, "updateRelations") or []
		new_teacher_ids = _find_key_by_prefix(new_data, "newRelationTeacherId") or []
		new_subject_ids = _find_key_by_prefix(new_data, "newRelationSubjectId") or []

		# --- relations (own row id): local -> id_prod ---
		update_local_ids = [r.get('id') for r in update_relations if r.get('id') is not None]
		all_relation_local_ids = list(set(delete_relation_ids + update_local_ids))
		relation_prod_map = _map_ids_to_prod(db, "relation_teacher_to_subject_group", "id", all_relation_local_ids)

		delete_relation_ids_prod = []
		for rid in delete_relation_ids:
			prod_id = relation_prod_map.get(rid)
			if prod_id is None:
				logger.warning("push_groupUpdate: no id_prod for delete relation local id %s, skipping", rid)
				continue
			delete_relation_ids_prod.append(prod_id)

		# --- teachers referenced inside updateRelations (teacherId) ---
		update_teacher_ids = [r.get('teacherId') for r in update_relations if r.get('teacherId') is not None]
		update_teacher_prod_map = _map_ids_to_prod(db, "user", "id", list(set(update_teacher_ids)))

		# --- subjects referenced inside updateRelations (subjectId) ---
		update_subject_ids = [r.get('subjectId') for r in update_relations if r.get('subjectId') is not None]
		update_subject_prod_map = _map_subject_ids_to_prod(db, list(set(update_subject_ids)))

		update_relations_prod = []
		for r in update_relations:
			rel_prod_id = relation_prod_map.get(r.get('id'))
			teacher_prod_id = update_teacher_prod_map.get(r.get('teacherId'))
			subject_prod_id = update_subject_prod_map.get(r.get('subjectId'))

			if rel_prod_id is None or teacher_prod_id is None or subject_prod_id is None:
			 logger.warning(
				"push_groupUpdate: missing id_prod for update relation %s (rel=%s teacher=%s subject=%s), skipping",
				r, rel_prod_id, teacher_prod_id, subject_prod_id
			 )
			 continue

			update_relations_prod.append({
			 "id": rel_prod_id,
			 "teacherId": teacher_prod_id,
			 "subjectId": subject_prod_id
		  })

		# --- newRelationTeacherId: local user id -> id_prod ---
		teacher_prod_map = _map_ids_to_prod(db, "user", "id", new_teacher_ids)
		new_teacher_ids_prod = []
		for tid in new_teacher_ids:
			prod_id = teacher_prod_map.get(tid)
			if prod_id is None:
				logger.warning("push_groupUpdate: no id_prod for teacher (user) local id %s, skipping", tid)
				continue
			new_teacher_ids_prod.append(prod_id)

		# --- newRelationSubjectId: local subject id -> id_prod ---
		subject_prod_map = _map_subject_ids_to_prod(db, new_subject_ids)
		new_subject_ids_prod = []
		for sid in new_subject_ids:
			prod_id = subject_prod_map.get(sid)
			if prod_id is None:
				logger.warning("push_groupUpdate: no id_prod for subject local id %s, skipping", sid)
				continue
			new_subject_ids_prod.append(prod_id)

		payload = {
		  "name": new_data.get('name'),
		  "capacity": new_data.get('capacity'),
		  "deleteRelationIds": delete_relation_ids_prod,
		  "updateRelations": update_relations_prod,
		  "newRelationTeacherId": new_teacher_ids_prod,
		  "newRelationSubjectId": new_subject_ids_prod
	   }

		print(payload)
		status, response_data = _send_update_group_api(settings, payload, group_id_prod, session_prodId, local_localId)

		if status:
			logger.info("Group updated remotely, local id %s -> prod id %s", group_id, group_id_prod)

		return status, response_data
	except Exception as e:
		logger.exception("Error in push_groupUpdate: %s", e)
		return False, None

def push_groupDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		groupId = old_data.get('id')
		sessionId = old_data.get('session_id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM relation_group_local_session WHERE id = %s""",
			(groupId,)
		)
		group_result = cursor.fetchone()
		cursor.close()

		if not group_result:
			logger.error("No id_prod found for group id %s", groupId)
			return False

		cursor = db.connection.cursor(dictionary=True)  # new cursor
		cursor.execute(
			"""SELECT id_prod FROM session WHERE id = %s""",
			(sessionId,)
		)
		session_result = cursor.fetchone()
		cursor.close()

		if not session_result:
			logger.error("No id_prod found for session id %s", sessionId)
			return False

		payload = {
			"group_id": group_result['id_prod'],
			"sessionId": session_result['id_prod'],
			"localId": old_data.get('local_id')
		}
		return _send_delete_group_api(settings, payload)

	except Exception as e:
		logger.exception("Error in push_groupDelete: %s", e)
		return False


# ==============================================
# STUDENT GROUP API
# ==============================================
def _send_affect_user_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = (
			f"{settings.api_base_url}/slc/group-assigned-student/"
			f"{payload.get('userId')}/{payload.get('groupId')}/"
			f"{payload.get('sessionId')}/{payload.get('localId')}"
		)
		body = {"relationId": payload.get('relationId')}
		response = requests.post(url, data=body, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Affected user - %s", response.text)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_affect_user_api: %s", e)
		return False

def _send_disaffect_user_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = (
			f"{settings.api_base_url}/slc/group-remove-student/"
			f"{payload.get('userId')}/{payload.get('sessionId')}/"
			f"{payload.get('localId')}"
		)
		body = {"relationId": payload.get('relationId')}
		response = requests.post(url, data=body, headers=headers, timeout=10)
		if response.status_code == 200:
			response_data = response.json()
			logger.info("Disaffected user - %s", response.text)
			return True
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False

	except Exception as e:
		logger.exception("Remote API error in _send_disaffect_user_api: %s", e)
		return False



def push_affect_user(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))

		# --- Local ID'S ---
		relation_local_id = new_data.get('relation_user_session_id')
		local_user_id = new_data.get('user_id')
		local_session_id = new_data.get('session_id')
		local_group_id = new_data.get('group_id')

		# --- User Prod Id
		user_id_map = _map_ids_to_prod(db, "user", "id", [local_user_id])
		prod_user_id = user_id_map.get(local_user_id)

		# --- Session Prod Id
		session_id_map = _map_ids_to_prod(db, "session", "id", [local_session_id])
		prod_session_id = session_id_map.get(local_session_id)

		# --- Group Prod Id
		group_id_map = _map_ids_to_prod(db, "relation_group_local_session", "id", [local_group_id])
		prod_group_id = group_id_map.get(local_group_id)

		# --- Relation Prod Id
		relation_id_map = _map_ids_to_prod(db, "relation_user_session", "id", [relation_local_id])
		prod_relation_id = relation_id_map.get(relation_local_id)

		# --- Local Prod Id
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT l.id as local_id
			   FROM local l, session s
			   WHERE s.account_id = l.account_id
			   AND s.id = %s
			""", (local_session_id,)
		)
		result = cursor.fetchone()
		cursor.close()
		if result is None:
			logger.error("No local found for session_id=%s", local_session_id)
			return False
		local_id = result['local_id']

		if None in (prod_user_id, prod_session_id, prod_group_id, prod_relation_id, local_id):
			logger.warning(
				"Skipping affect push, missing id mapping: user=%s session=%s group=%s relation=%s local=%s",
				prod_user_id, prod_session_id, prod_group_id, prod_relation_id, local_id
			)
			return False

		payload = {
			"userId": prod_user_id,
			"groupId": prod_group_id,
			"sessionId": prod_session_id,
			"localId": local_id,
			"relationId": prod_relation_id
		}
		result_send = _send_affect_user_api(settings, payload)

		return result_send
	except Exception as e:
		logger.exception("Error in push_affect_user: %s", e)
		return False

def push_disaffect_user(db,settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))

		# --- Local ID'S ---
		relation_local_id = new_data.get('relation_user_session_id')
		local_user_id = new_data.get('user_id')
		local_session_id = new_data.get('session_id')

		# --- User Prod Id
		user_id_map = _map_ids_to_prod(db, "user", "id", [local_user_id])
		prod_user_id = user_id_map.get(local_user_id)

		# --- Session Prod Id
		session_id_map = _map_ids_to_prod(db, "session", "id", [local_session_id])
		prod_session_id = session_id_map.get(local_session_id)

		# --- Relation Prod Id
		relation_id_map = _map_ids_to_prod(db, "relation_user_session", "id", [relation_local_id])
		prod_relation_id = relation_id_map.get(relation_local_id)

		# --- Local Prod Id
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("""
			SELECT l.id as local_id
			FROM local l, session s
			WHERE s.account_id = l.account_id
			AND s.id = %s
		""", (local_session_id,))
		result = cursor.fetchone()
		cursor.close()
		if result is None:
			logger.error("No local found for session_id = %s", local_session_id)
			return False
		local_id = result['local_id']

		if None in(prod_user_id, prod_session_id, prod_relation_id, local_id):
			logger.warning("Skipping disaffect, Missing id mapping: user%s session:%s relation=%s local=%s",
						   prod_user_id, prod_session_id, prod_relation_id, local_id)
			return False

		# --- data to send to the function
		payload = {
			"userId": prod_user_id,
			"sessionId": prod_session_id,
			"localId": local_id,
			"relationId": prod_relation_id
		}
		# --- function to send to remote server
		result_send = _send_disaffect_user_api(settings, payload)
		return result_send
	except Exception as e:
		logger.exception("Error in push_disaffect_user: %s", e)
		return False
