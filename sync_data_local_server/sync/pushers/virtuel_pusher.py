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
def _send_create_virtuelUser_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-virtual-student"
		logger.debug("POST %s | payload: %s", url, payload)
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None, None

			virtuelUser = response_data.get('student', {}).get('id')
			userId = response_data.get('student', {}).get('userId')
			if virtuelUser is None or userId is None:
				logger.error("Missing id/userId in response_data['student']: %s", response_data)
				return False, None, None

			return True, virtuelUser, userId

		elif response.status_code == 400:
			logger.error("Bad request response: %s", response.text)
			return False, None, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None, None

	except Exception as e:
		logger.error("Exception in _send_create_virtuelUser_api: %s", e)
		return False, None, None

def _send_update_virtuelUser_api(settings, payload):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/update-virtual-student"
        logger.debug("POST %s | payload: %s", url, payload)
        response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info("Virtual user updated successfully on remote: %s", response_data)
                return True
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False
        else:
            logger.error(
                "Failed to update virtual user. Status: %s | Response: %s",
                response.status_code, response.text
            )
            return False

    except requests.exceptions.RequestException as e:
        logger.error("Request error while updating virtual user: %s", e)
        return False
    except Exception as e:
        logger.error("Unexpected error while updating virtual user: %s", e)
        return False

def _send_delete_virtuelUser_api(settings, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-virtual-student"
		logger.debug("POST %s | payload: %s", url, payload)
		response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Virtual user deleted successfully on remote: %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error(
				"Failed to update virtual user. Status: %s | Response: %s",
				response.status_code, response.text
			)
			return False

	except Exception as e:
		return False




def push_virtuelAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		idVlocal = new_data.get('virtual_user_id')
		idUlocal = new_data.get('id')
		phone = new_data.get('phone')
		full_name = new_data.get('full_name')
		email = new_data.get('email')
		status = new_data.get('status')

		payload = {
			"name":   full_name,
			"phone":  phone,
			"email":  email,
			"status": status
		}

		api_status, virtuelId, userId = _send_create_virtuelUser_api(settings, payload)

		if api_status and virtuelId:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE virtual_user SET id_prod = %s WHERE id = %s",
				(virtuelId, idVlocal)
			)
			cursor.execute(
				"UPDATE user SET id_prod = %s WHERE id = %s",
				(userId, idUlocal)
			)
			db.connection.commit()
			cursor.close()
			logger.info("User and virtual user updated: userId=%s virtualId=%s", idUlocal, idVlocal)

		return api_status

	except Exception as e:
		logger.error("Error coming from push_virtuelAdd: %s", e)
		return False

def push_virtuelUpdate(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data', '{}'))

        # --- Local ID'S ---
        virtuel_user_local_id = new_data.get('id')
        name          = new_data.get('name')
        phone         = new_data.get('phone')
        email         = new_data.get('email')
        status        = new_data.get('user_id')
        local_user_id = new_data.get('user_id')
        account_id    = new_data.get('account_id')

        # --- Virtuel User Prod Id
        virtuelUser_id_map = _map_ids_to_prod(db, "virtual_user", "id", [virtuel_user_local_id])
        prod_virtuelUser_id = virtuelUser_id_map.get(virtuel_user_local_id)

        # --- USER Prod Id
        user_id_map = _map_ids_to_prod(db, "user", "id", [local_user_id])
        prod_user_id = user_id_map.get(local_user_id)

        payload ={
            "id":     prod_virtuelUser_id,
            "userId": prod_user_id,
            "name":   name,
            "phone":  phone,
            "email":  email,
            "status": status
        }

        result_send = _send_update_virtuelUser_api(settings, payload)
        return result_send

    except Exception as e:
        return  False


def push_virtuelDelete(db, settings, row):
	try:
		old_data             = json.loads(row.get('old_data', '{}'))

		# --- Local ID'S ---
		local_user_id        = old_data.get('user_id')
		local_virtuelUser_id = old_data.get('id')
		account_id           = old_data.get('account_id')

		# --- Virtuel User Prod Id
		virtuelUser_id_map = _map_ids_to_prod(db, "virtual_user", "id", [local_virtuelUser_id])
		prod_virtuelUser_id = virtuelUser_id_map.get(local_virtuelUser_id)

		# --- USER Prod Id
		user_id_map = _map_ids_to_prod(db, "user", "id", [local_user_id])
		prod_user_id = user_id_map.get(local_user_id)

		payload = {
			"id": prod_virtuelUser_id,
			"prod_user_id": prod_user_id
		}
		result_send = _send_delete_virtuelUser_api(settings, payload)

	except Exception as e:
		return False
