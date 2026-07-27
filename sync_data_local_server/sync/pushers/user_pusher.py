import logging
import os
import sys
import json
import requests
from core.auth import get_token
from utils.helpers import _map_ids_to_prod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

def _send_create_student_api(db, settings, new_data, account_id):
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

        logger.debug("POST %s | payload: %s", url, payload)
        response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                print("\n \n \n \n \n \n \n \n ", response_data)
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

        # Send roles as repeated form keys: roles[0], roles[1]...
        for i, role in enumerate(roles):
            payload.append((f"roles[{i}]", role))

        # Optional image upload
        files = {}
        img_link = new_data.get("img_link")
        image_fp = None
        if img_link:
            local_path = os.path.join(settings.upload_root, img_link.lstrip("/"))
            if os.path.exists(local_path):
                image_fp = open(local_path, "rb")
                files["image"] = (os.path.basename(local_path), image_fp, "image/jpeg")

        logger.debug("POST %s | payload: %s | roles: %s", url, payload, roles)

        response = requests.post(
            url, data=payload, files=files if files else None,
            headers=headers, verify=False, timeout=(5, 30)
        )

        if image_fp:
            image_fp.close()

        if response.status_code == 200:
            try:
                response_data = response.json()
                return True, response_data.get("data", {})
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
        image_fp = None
        if img_link:
            local_path = os.path.join(settings.upload_root, img_link.lstrip("/"))
            if os.path.exists(local_path):
                image_fp = open(local_path, "rb")
                files["image"] = (os.path.basename(local_path), image_fp, "image/jpeg")

        logger.debug("POST %s | payload: %s", url, payload)

        response = requests.post(
            url, data=payload, files=files if files else None,
            headers=headers, verify=False, timeout=10
        )

        if image_fp:
            image_fp.close()

        if response.status_code == 200:
            try:
                response_data = response.json()
                return True, response_data.get("data", {})
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
        else:
            logger.error("Create teacher failed %s: %s", response.status_code, response.text)
            return False, None
    except Exception as e:
        logger.exception("Remote API error in create teacher: %s", e)
        return False, None

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
        print("\n \n \n \n processing techer add")
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
            return False

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
            remote_id = result  # student pusher still returns a flat id
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
        new_data         = json.loads(row.get('payload', '{}'))
        local_user_id    = new_data.get('user_id')
        local_virtuel_id = new_data.get('virtual_user_id')


        if not local_user_id or not local_virtuel_id:
            logger.error("push_userAssociation: missing user_id or virtual_user_id in payload")
            return False

        local_user_id    = int(local_user_id)
        local_virtuel_id = int(local_virtuel_id)


        user_prod_map    = _map_ids_to_prod(db, "user", "id", [local_user_id])
        virtual_prod_map = _map_ids_to_prod(db, "virtual_user", "id", [local_virtuel_id])

        remote_user_id    = user_prod_map.get(local_user_id)
        remote_virtuel_id = virtual_prod_map.get(local_virtuel_id)

        print("\n ======================================================= \n")
        print("Remote User Id: ", remote_user_id)
        print("Remote VirtuelUser Id: ", remote_virtuel_id)
        print("\n ======================================================= \n")

        if not remote_user_id or not remote_virtuel_id:
            logger.error(
                "push_userAssociation: missing id_prod for user_id=%s (got %s) or virtual_id=%s (got %s)",
                local_user_id, remote_user_id, local_virtuel_id, remote_virtuel_id
            )
            return False

        payload = {
            "userId": remote_user_id,
            "virtualUserId": remote_virtuel_id
        }

        status, result = _send_associate_user_api(settings, payload)
        return status

    except Exception as e:
        logger.error("Error coming from push_userAssociation: %s", e)
        return False