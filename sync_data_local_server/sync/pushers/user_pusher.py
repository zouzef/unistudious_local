import logging
import os
import sys
import json
import shutil
import requests
from core.auth import get_token
from utils.helpers import _map_ids_to_prod
import mimetypes


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

# Remote understood the request and refused the data -> undo the local action, no retry
REJECT_CODES = {400, 409, 422}
LOCAL_UPLOADS_PATH = "../server_local_api/uploads/user_img"


def _rejected(response):
	"""Returned instead of None when the remote refuses the data."""
	return {
		"rejected": True,
		"status_code": response.status_code,
		"reason": response.text,
	}


# ─────────────────────────────────────────────
# Local rollback
# ─────────────────────────────────────────────

def _rollback_local_user(db, local_id, role):
	"""Delete the local user (and relations) that the remote refused.
	Only deletes when id_prod IS NULL, so an already-synced user is never removed."""
	cursor = None
	try:
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute("SELECT id_prod FROM user WHERE id = %s", (local_id,))
		row = cursor.fetchone()
		if not row:
			logger.warning("Rollback: local user id=%s already gone", local_id)
			return True
		if row.get("id_prod"):
			logger.error("Rollback skipped: user id=%s already has id_prod=%s", local_id, row["id_prod"])
			return False

		if role == "ROLE_TEACHER":
			cursor.execute("DELETE FROM relation_teacher_account WHERE user_id = %s", (local_id,))

		cursor.execute("DELETE FROM user WHERE id = %s AND id_prod IS NULL", (local_id,))
		db.connection.commit()

		user_dir = os.path.join(LOCAL_UPLOADS_PATH, f"user_{local_id}")
		if os.path.isdir(user_dir):
			shutil.rmtree(user_dir, ignore_errors=True)

		logger.warning("🗑️ Local user id=%s (role=%s) deleted: remote rejected it", local_id, role)
		return True
	except Exception as e:
		db.connection.rollback()
		logger.exception("Rollback failed for local user id=%s: %s", local_id, e)
		return False
	finally:
		if cursor:
			cursor.close()


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

# ───────────────────────────────────────────── Create API  ─────────────────────────────────────────────
def _send_create_student_api(db, settings, new_data, account_id):
	image_fp = None
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-platform-student"

		local_session_ids = new_data.get("sessions", [])

		session_ids = []
		if local_session_ids:
			placeholders = ", ".join(["%s"] * len(local_session_ids))
			session_query = f"""
				SELECT id_prod
				FROM session
				WHERE id IN ({placeholders})
				  AND enabled = 1
				  AND account_id = %s
			"""
			session_rows = db.fetch_query(session_query, local_session_ids + [account_id])
			session_ids = [row["id_prod"] for row in session_rows if row.get("id_prod")]

		payload = [
			("fullName",     new_data.get("full_name")),
			("username",     new_data.get("username")),
			("email",        new_data.get("email")),
			("password",     new_data.get("password")),
			("phone_number", new_data.get("phone")),
			("location",     new_data.get("address")),
		]

		for i, session_id in enumerate(session_ids):
			payload.append((f"sessions[{i}]", session_id))

		files = {}
		img_link = new_data.get("img_link")
		local_user_id = new_data.get("id")

		if img_link and local_user_id:
			local_path = os.path.join(LOCAL_UPLOADS_PATH, f"user_{local_user_id}", img_link)

			logger.debug("Resolved student image path: %s | exists: %s", local_path, os.path.exists(local_path))
			if os.path.exists(local_path):
				mime_type, _ = mimetypes.guess_type(local_path)
				image_fp = open(local_path, "rb")
				files["image"] = (os.path.basename(local_path), image_fp, mime_type or "application/octet-stream")
			else:
				logger.warning("Student image not found on disk: %s", local_path)

		logger.debug("POST %s | payload: %s | files: %s", url, payload, list(files.keys()))
		response = requests.post(
			url, data=payload, files=files if files else None,
			headers=headers, verify=False, timeout=10
		)

		if response.status_code == 200:
			try:
				response_data = response.json()
				remote_id = response_data.get("data", {}).get("id")
				return True, remote_id
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
		elif response.status_code in REJECT_CODES:
			logger.error("Create student REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		else:
			logger.error("Create student failed %s: %s", response.status_code, response.text)
			return False, None
	except Exception as e:
		logger.exception("Remote API error in create student: %s", e)
		return False, None
	finally:
		if image_fp:
			image_fp.close()


def _send_create_manager_api(settings, new_data):
	image_fp = None
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-manager"

		roles = new_data.get("roles", "ROLE_MANAGER_ADMINISTRATIVE")
		if isinstance(roles, str):
			try:
				roles = json.loads(roles)
			except Exception:
				roles = [roles]
		elif not isinstance(roles, list):
			roles = [roles]

		payload = [
			("fullName",     new_data.get("full_name")),
			("username",     new_data.get("username")),
			("email",        new_data.get("email")),
			("password",     new_data.get("password")),
			("phone_number", new_data.get("phone")),
			("location",     new_data.get("address")),
		]

		for i, role in enumerate(roles):
			payload.append((f"roles[{i}]", role))

		files = {}
		photo_path = new_data.get("photo")
		if photo_path and os.path.exists(photo_path):
			image_fp = open(photo_path, "rb")
			files["image"] = (os.path.basename(photo_path), image_fp, "image/jpeg")

		logger.debug("POST %s | payload: %s | roles: %s", url, payload, roles)

		response = requests.post(
			url, data=payload, files=files if files else None,
			headers=headers, verify=False, timeout=(5, 30)
		)

		if response.status_code == 200:
			try:
				response_data = response.json()
				return True, response_data.get("data", {})
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
		elif response.status_code in REJECT_CODES:
			logger.error("Create manager REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		else:
			logger.error("Create manager failed %s: %s", response.status_code, response.text)
			return False, None
	except Exception as e:
		logger.exception("Remote API error in create manager: %s", e)
		return False, None
	finally:
		if image_fp:
			image_fp.close()


def _send_create_teacher_api(settings, new_data):
	image_fp = None
	try:
		token   = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url     = f"{settings.api_base_url}/slc/create-teacher"

		payload = [
			("fullName",     new_data.get("full_name")),
			("username",     new_data.get("username")),
			("email",        new_data.get("email")),
			("password",     new_data.get("password")),
			("phone_number", new_data.get("phone")),
			("location",     new_data.get("address")),
			("account_id",   new_data.get("account_id")),
		]

		permissions = new_data.get("allowedPermissionAccess", []) or []
		sessions    = new_data.get("allowedAccessSession", []) or []

		for i, perm in enumerate(permissions):
			payload.append((f"allowedPermissionAccess[{i}]", perm))
		for i, sess in enumerate(sessions):
			payload.append((f"allowedAccessSession[{i}]", sess))

		files = {}
		img_link = new_data.get("img_link")
		local_user_id = new_data.get("id")

		if img_link and local_user_id:
			local_path = os.path.join(LOCAL_UPLOADS_PATH, f"user_{local_user_id}", img_link)

			logger.debug("Resolved teacher image path: %s | exists: %s", local_path, os.path.exists(local_path))
			if os.path.exists(local_path):
				mime_type, _ = mimetypes.guess_type(local_path)
				image_fp = open(local_path, "rb")
				files["image"] = (os.path.basename(local_path), image_fp, mime_type or "application/octet-stream")
			else:
				logger.warning("Teacher image not found on disk: %s", local_path)

		logger.debug("POST %s | payload: %s | files: %s", url, payload, list(files.keys()))

		response = requests.post(
			url, data=payload, files=files if files else None,
			headers=headers, verify=False, timeout=10
		)

		if response.status_code == 200:
			try:
				response_data = response.json()
				return True, response_data.get("data", {})
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
		elif response.status_code in REJECT_CODES:
			logger.error("Create teacher REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		else:
			logger.error("Create teacher failed %s: %s", response.status_code, response.text)
			return False, None

	except Exception as e:
		logger.exception("Remote API error in create teacher: %s", e)
		return False, None

	finally:
		if image_fp:
			image_fp.close()


def _send_associate_user_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/associate-virtual-user"
		response = requests.post(
			url,
			data=payload,
			headers=headers,
			verify=False,
			timeout=10
		)
		if response.status_code == 200:
			try:
				response_data = response.json()
				return True, response_data.get("data", {})
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
		else:
			logger.error("Associate Virtueluser with User failed %s: %s", response.status_code, response.text)
			return False, None
	except Exception as e:
		logger.error("Error: %s", e)
		return False, None


# ───────────────────────────────────────────── Update API  ─────────────────────────────────────────────
def _send_update_Manager_api(settings, row, url):
	try:
		logger.debug(f"_send_update_Manager_api called with url={url}, row_id={row.get('id')}")

		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		roles_raw = row.get('roles', '[]')

		if isinstance(roles_raw, str):
			roles_list = json.loads(roles_raw)
		else:
			roles_list = roles_raw or []

		logger.debug(f"roles_raw={roles_raw}, parsed roles_list={roles_list}")

		payload = {
			"fullName":     row.get('full_name'),
			"username":     row.get('username'),
			"email":        row.get('email'),
			"location":     row.get('address'),
			"phone_number": row.get('phone'),
			"roles[]":      roles_list,
		}

		password = row.get('password')
		if password:
			payload["password"] = password
			logger.debug("password included in payload")

		logger.debug(f"payload built (before files): {payload}")

		files = None
		image_path = row.get('photo')

		if image_path and os.path.isfile(image_path):
			logger.debug(f"attaching image from image_path={image_path}")
			f = open(image_path, 'rb')
			files = {
				"image": (os.path.basename(image_path), f, "image/jpeg")
			}
		else:
			logger.debug(f"no image attached, image_path={image_path}")

		try:
			logger.debug(f"sending POST to {url}")
			response = requests.post(
				url,
				data=payload,
				files=files,
				headers=headers,
				verify=False,
				timeout=10
			)
			logger.debug(f"response status_code={response.status_code}")
		finally:
			if files:
				files["image"][1].close()

		if response.status_code == 200:
			try:
				response_json = response.json()
				logger.debug(f"update manager success, response.json()={response_json}")
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Update manager failed %s: %s", response.status_code, response.text)
			return False

	except Exception as e:
		logger.exception("Error in _send_update_Manager_api: %s", e)
		return False


# ───────────────────────────────────────────── Delete API  ─────────────────────────────────────────────
def _send_delete_Manager_api(settings, row, url):
	try:
		logger.debug(f"_send_delete_Manager_api called with url={url}, row_id={row.get('id')}")

		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}

		logger.debug(f"sending POST to {url}")
		response = requests.post(url, headers=headers, verify=False, timeout=10)
		logger.debug(f"response status_code={response.status_code}")

		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.debug(f"delete manager success, response.json()={response_data}")
				return True
			except Exception as e:
				logger.error(f"Invalid JSON response in delete manager: {e}, raw text={response.text}")
				return False
		else:
			logger.error("Delete manager failed %s: %s", response.status_code, response.text)
			return False

	except Exception as e:
		logger.exception("Error in _send_delete_Manager_api: %s", e)
		return False


# ─────────────────────────────────────────────
# Push functions (called by pusher dispatcher)
# ─────────────────────────────────────────────

MANAGER_ROLES = {
	"ROLE_MANAGER_CONFIG",
	"ROLE_MANAGER_FINANCE",
	"ROLE_MANAGER_HR",
	"ROLE_MANAGER_IT",
	"ROLE_MANAGER_MARKETING",
	"ROLE_CUSTOMER_MANAGER_SERVICE",
	"ROLE_MANAGER_ADMINISTRATIVE",
}


def _route_create(role, settings, new_data, db):
	if role == "ROLE_TEACHER":
		return _send_create_teacher_api(settings, new_data)
	elif role in MANAGER_ROLES:
		return _send_create_manager_api(settings, new_data)
	else:
		account_id = new_data.get("account_id")
		return _send_create_student_api(db, settings, new_data, account_id)


def push_userAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('payload', '{}'))
		role     = row.get('role', 'ROLE_USER')
		local_id = new_data.get('id')
		status, result = _route_create(role, settings, new_data, db)

		if not status:
			# Remote refused the data -> undo the local action
			if isinstance(result, dict) and result.get("rejected"):
				logger.error(
					"Remote rejected user local=%s role=%s [%s]: %s",
					local_id, role, result.get("status_code"), result.get("reason")
				)
				_rollback_local_user(db, local_id, role)
				return True  # handled: the audit row must not be retried
			return False  # network / 5xx / auth error: retry later

		cursor = db.connection.cursor(dictionary=True)

		if role == "ROLE_TEACHER":
			teacher_remote_id = result.get("teacher", {}).get("id") if isinstance(result, dict) else None
			relation_remote_id = result.get("relationTeacherAccount", {}).get("id") if isinstance(result, dict) else None

			if teacher_remote_id:
				cursor.execute(
					"UPDATE user SET id_prod = %s WHERE id = %s",
					(teacher_remote_id, local_id)
				)
			if relation_remote_id:
				cursor.execute(
					"UPDATE relation_teacher_account SET id_prod = %s WHERE user_id = %s",
					(relation_remote_id, local_id)
				)
			db.connection.commit()
			logger.info("✅ Teacher synced: local=%s remote=%s relation_id_prod=%s",
						local_id, teacher_remote_id, relation_remote_id)

		elif role in MANAGER_ROLES:
			manager_remote_id = result.get("id") if isinstance(result, dict) else None
			if manager_remote_id:
				cursor.execute(
					"UPDATE user SET id_prod = %s WHERE id = %s",
					(manager_remote_id, local_id)
				)
				db.connection.commit()
				logger.info("✅ Manager synced: local=%s remote=%s", local_id, manager_remote_id)

		else:
			remote_id = result  # student pusher returns a flat id
			if remote_id:
				cursor.execute(
					"UPDATE user SET id_prod = %s WHERE id = %s",
					(remote_id, local_id)
				)
				db.connection.commit()
				logger.info("✅ User synced: local=%s remote=%s role=%s", local_id, remote_id, role)

		cursor.close()
		return status
	except Exception as e:
		logger.exception("Error in push_userAdd: %s", e)
		return False


def push_userUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('payload', '{}'))
		role     = row.get('role', 'ROLE_USER')
		local_id = new_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM user WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()
		if not result or not result.get('id_prod'):
			logger.error("❌ No id_prod found for local user id=%s, skipping update", local_id)
			return False

		id_prod = result['id_prod']

		if role == "ROLE_TEACHER":
			url = f"{settings.api_base_url}/slc/update-teacher/{id_prod}"
		elif role in MANAGER_ROLES:
			url = f"{settings.api_base_url}/slc/update-manager/{id_prod}"
			manager_data = json.loads(row.get('payload', '{}'))
			return _send_update_Manager_api(settings, manager_data, url)
		else:
			url = f"{settings.api_base_url}/slc/update-platform-student/{id_prod}"

		payload = {
			"fullName":     new_data.get("full_name"),
			"phone_number": new_data.get("phone"),
			"location":     new_data.get("address"),
			"status":       new_data.get("status"),
		}

		token    = get_token()
		headers  = {"Authorization": f"Bearer {token}"}
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			logger.info("✅ User updated remote: local=%s remote=%s", local_id, id_prod)
			return True
		else:
			logger.error("❌ Update failed %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Error in push_userUpdate: %s", e)
		return False


def push_userDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('payload', '{}'))
		role     = row.get('role', 'ROLE_USER')
		local_id = old_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM user WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result or not result.get('id_prod'):
			logger.error("❌ No id_prod found for local user id=%s, skipping delete", local_id)
			return False

		id_prod = result['id_prod']
		if role == "ROLE_TEACHER":
			url = f"{settings.api_base_url}/slc/delete-teacher/{id_prod}"
		elif role in MANAGER_ROLES:
			url = f"{settings.api_base_url}/slc/delete-manager/{id_prod}"
			return _send_delete_Manager_api(settings, row, url)
		else:
			url = f"{settings.api_base_url}/slc/delete-platform-student/{id_prod}"

		token    = get_token()
		headers  = {"Authorization": f"Bearer {token}"}
		response = requests.post(url, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			logger.info("✅ User deleted remote: local=%s remote=%s", local_id, id_prod)
			return True
		else:
			logger.error("❌ Delete failed %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Error in push_userDelete: %s", e)
		return False


def push_userAssociation(db, settings, row):
	try:
		new_data            = json.loads(row.get('payload', '{}'))
		local_user_id       = new_data.get('user_id')
		local_virtuel_id    = new_data.get('virtual_user_id')
		old_virtual_user_id = new_data.get('old_virtual_user_id')

		if not local_user_id or not local_virtuel_id or not old_virtual_user_id:
			logger.error("push_userAssociation: missing user_id, virtual_user_id or old_virtual_user_id in payload")
			return False

		local_user_id       = int(local_user_id)
		old_virtual_user_id = int(old_virtual_user_id)

		user_prod_map  = _map_ids_to_prod(db, "user", "id", [local_user_id])
		remote_user_id = user_prod_map.get(local_user_id)

		old_virtual_user_id_map = _map_ids_to_prod(db, "user", "id", [old_virtual_user_id])
		remote_id_user_virtual  = old_virtual_user_id_map.get(old_virtual_user_id)

		if not remote_user_id or not remote_id_user_virtual:
			logger.error(
				"push_userAssociation: missing id_prod for user_id=%s (got %s) or virtual_id=%s (got %s)",
				local_user_id, remote_user_id, old_virtual_user_id, remote_id_user_virtual
			)
			return False

		payload = {
			"virtualId": remote_id_user_virtual,
			"realUserId": remote_user_id
		}
		status, result = _send_associate_user_api(settings, payload)
		return status

	except Exception as e:
		logger.error("Error coming from push_userAssociation: %s", e)
		return False