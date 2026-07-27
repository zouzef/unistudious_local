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

def _send_associate_virtuelUser_api(settings, payload):
    try:
       token = get_token()
       headers = {"Authorization": f"Bearer {token}"}
       url = f"{settings.api_base_url}/slc/save-virtual-student-sessions"

       form_data = {"userId": payload["userId"]}
       for i, session_id in enumerate(payload["sessionIds"]):
          form_data[f"sessionIds[{i}]"] = session_id

       logger.debug("POST %s | payload: %s", url, form_data)
       response = requests.post(url, data=form_data, headers=headers, verify=False, timeout=10)

       if response.status_code == 200:

          try:
             response_data = response.json()
             logger.debug("Response: %s", response_data)
          except Exception:
             logger.error("Invalid JSON response: %s", response.text)
             return False

          if not response_data.get('success'):
             logger.error("API returned success=false: %s", response_data)
             return False

          return True

       elif response.status_code == 400:
          logger.error("Bad request response: %s", response.text)
          return False
       else:
          logger.error("Unexpected status %s: %s", response.status_code, response.text)
          return False

    except Exception as e:
       logger.error("Exception in _send_associate_virtuelUser_api: %s", e)
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

def push_virtuelAssociate(db, settings, row):
    try:
       new_data     = json.loads(row.get('new_data', '{}'))
       user_id      = new_data.get('user_id')
       account_id   = new_data.get('account_id')
       session_ids  = new_data.get('session_ids') or []
       relations_by_session = new_data.get('relations_by_session') or {}

       if not user_id or not session_ids:
          logger.error("push_virtuelAssociate: missing user_id or session_ids in new_data")
          return False

       cursor = db.connection.cursor(dictionary=True)

       # Resolve remote id_prod for the user
       cursor.execute("SELECT id_prod FROM user WHERE id = %s", (user_id,))
       user_row = cursor.fetchone()
       if not user_row or not user_row.get('id_prod'):
          logger.error("push_virtuelAssociate: no id_prod found for user_id=%s", user_id)
          cursor.close()
          return False
       remote_user_id = user_row['id_prod']

       # Resolve remote id_prod for each session
       remote_session_ids = []
       for session_id in session_ids:
          cursor.execute("SELECT id_prod FROM session WHERE id = %s", (session_id,))
          session_row = cursor.fetchone()
          if not session_row or not session_row.get('id_prod'):
             logger.error("push_virtuelAssociate: no id_prod found for session_id=%s", session_id)
             cursor.close()
             return False
          remote_session_ids.append(session_row['id_prod'])

       cursor.close()

       payload = {
          "userId": remote_user_id,
          "sessionIds": remote_session_ids
       }

       api_status = _send_associate_virtuelUser_api(settings, payload)

       if api_status:
          logger.info("Sessions associated remotely: user_id=%s session_ids=%s", user_id, session_ids)

       return api_status

    except Exception as e:
       logger.error("Error coming from push_virtuelAssociate: %s", e)
       return False