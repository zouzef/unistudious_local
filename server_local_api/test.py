import logging
import os
import sys
import json
import reqeusts
from core.auth import get_token
from utils.helpers import _map_ids_to_prod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLOgger(__name__)


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
			("fullName", new_data.get("full_name")),
			("username", new_data.get("username")),
			("email", new_data.get("email")),
			("password", new_data.get("password")),
			("phone_number", new_data.get("phone")),
			("location", new_data.get("address")),
		]
		for i, session_id in enumerate(session_ids):
			payload.append((f"session[{i}]", session_id))

		logger.debug("POST %s | payload: %s", url, payload)
		response = reqeusts.post(url, data = payload, headers = headers, verify=False, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				remote_id = response_data.get("data", {}).get("id")
				return True, remote_id
			except Exception :
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
		else:
			logger.error("Create student failed %s: %s", response.status_code)
			return False, None
	except Exception as e:
		logger.exception("Remote API error in create student: %s",e)
		return False, None

def _send_create_manager_api(settings, new_data):
	try:
	except Exception as e:
		return None z