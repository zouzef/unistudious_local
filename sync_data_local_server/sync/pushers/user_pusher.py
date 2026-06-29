import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

def _send_create_student_api(settings, new_data):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-platform-student"

        payload = {
            "fullName":     new_data.get("full_name"),
            "username":     new_data.get("username"),
            "email":        new_data.get("email"),
            "password":     new_data.get("password"),
            "phone_number": new_data.get("phone"),
            "location":     new_data.get("address"),
        }

        logger.debug("POST %s | payload: %s", url, payload)
        response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                remote_id = response_data.get("data", {}).get("id")
                return True, remote_id
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
        else:
            logger.error("Create student failed %s: %s", response.status_code, response.text)
            return False, None
    except Exception as e:
        logger.exception("Remote API error in create student: %s", e)
        return False, None


def _send_create_manager_api(settings, new_data):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-manager"

        # roles can be a JSON string like '["ROLE_MANAGER_ADMINISTRATIVE"]' or plain string
        roles = new_data.get("roles", "ROLE_MANAGER_ADMINISTRATIVE")
        if isinstance(roles, str):
            try:
                roles = json.loads(roles)  # parse if stored as JSON string
            except Exception:
                roles = [roles]

        # form-data supports repeated keys for arrays
        payload = {
            "fullName":     new_data.get("full_name"),
            "username":     new_data.get("username"),
            "email":        new_data.get("email"),
            "password":     new_data.get("password"),
            "phone_number": new_data.get("phone"),
            "location":     new_data.get("address"),
        }

        # Send roles as repeated form keys: roles[0], roles[1]...
        files = []
        for i, role in enumerate(roles):
            files.append((f"roles[{i}]", (None, role)))

        logger.debug("POST %s | payload: %s | roles: %s", url, payload, roles)
        response = requests.post(url, data=payload, files=files, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                remote_id = response_data.get("data", {}).get("id")
                return True, remote_id
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
        else:
            logger.error("Create manager failed %s: %s", response.status_code, response.text)
            return False, None
    except Exception as e:
        logger.exception("Remote API error in create manager: %s", e)
        return False, None


def _send_create_teacher_api(settings, new_data):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-teacher"

        payload = {
            "fullName":     new_data.get("full_name"),
            "username":     new_data.get("username"),
            "email":        new_data.get("email"),
            "password":     new_data.get("password"),
            "phone_number": new_data.get("phone"),
            "location":     new_data.get("address"),
        }

        logger.debug("POST %s | payload: %s", url, payload)
        response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                # Teacher response is nested under data.teacher
                remote_id = response_data.get("data", {}).get("teacher", {}).get("id")
                return True, remote_id
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
        else:
            logger.error("Create teacher failed %s: %s", response.status_code, response.text)
            return False, None
    except Exception as e:
        logger.exception("Remote API error in create teacher: %s", e)
        return False, None


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

def _route_create(role, settings, new_data):
	"""Route to the correct remote create API based on role."""
	print("\n \n \n ",role)
	if role == "ROLE_TEACHER":
		print("\n \n \n \n processing techer add")
		return _send_create_teacher_api(settings, new_data)
	elif role in MANAGER_ROLES:
		return _send_create_manager_api(settings, new_data)
	else:
		# Default: ROLE_USER / student
		return _send_create_student_api(settings, new_data)


def push_userAdd(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data', '{}'))
        role     = row.get('role', 'ROLE_USER')
        local_id = new_data.get('id')

        status, remote_id = _route_create(role, settings, new_data)

        if status and remote_id:
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute(
                "UPDATE user SET id_prod = %s WHERE id = %s",
                (remote_id, local_id)
            )
            db.connection.commit()
            cursor.close()
            logger.info("✅ User synced: local=%s remote=%s role=%s", local_id, remote_id, role)

        return status
    except Exception as e:
        logger.exception("Error in push_userAdd: %s", e)
        return False


def push_userUpdate(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data', '{}'))
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

        # Update endpoints per role — adjust these once you have the remote docs
        if role == "ROLE_TEACHER":
            url = f"{settings.api_base_url}/slc/update-teacher/{id_prod}"
        elif role in MANAGER_ROLES:
            url = f"{settings.api_base_url}/slc/update-manager/{id_prod}"
        else:
            url = f"{settings.api_base_url}/slc/update-platform-student/{id_prod}"

        payload = {
            "fullName":     new_data.get("full_name"),
            "phone_number": new_data.get("phone"),
            "location":     new_data.get("address"),
            "status":       new_data.get("status"),
        }

        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
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
        old_data = json.loads(row.get('old_data', '{}'))
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
        else:
            url = f"{settings.api_base_url}/slc/delete-platform-student/{id_prod}"

        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
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