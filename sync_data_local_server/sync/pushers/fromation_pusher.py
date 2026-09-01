import logging
import os
import sys
import json
import requests
from core.auth import get_token


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

def _send_create_formation_api(settings, payload):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-formation"
        logger.debug("POST %s | payload: %s", url, payload)
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None

            if not response_data.get('status'):
                logger.error("API returned status=false: %s", response_data)
                return False, None

            formation_data = response_data.get('data') or {}
            formation_id = formation_data.get('id')

            if formation_id is None:
                logger.error("No 'id' in response data: %s", response_data)
                return False, None

            logger.info("Formation created - id %s", formation_id)
            return True, formation_id
        elif response.status_code == 400:
            logger.error("Api Error 400: %s", response.text)
            return False, None
        elif response.status_code == 403:
            logger.error("Access denied (403): %s", response.text)
            return False, None
        else:
            logger.error("Unexpected status %s: %s", response.status_code, response.text)
            return False, None
    except requests.exceptions.Timeout:
        logger.error("Request timeout (10s) — %s", url)
        return False, None
    except Exception as e:
        logger.exception("Remote API error in create Formation: %s", e)
        return False, None

def _send_update_formation_api(settings, payload, formationId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-formation/{formationId}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Formation updated - %s",response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s",response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_update_formation_api: %s", e)
		return False
	except Exception as e:
		logger.exception("Remote API error in _send_update_formation: %s", e)
		return False

def _send_delete_formation_api(settings, formationId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-formation/{formationId}"
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Formation delete - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s",response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
	except Exception as e:
		logger.exception("Remote API error in _send_delete_formation_api: %s",e)
		return False


def push_formationAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		Name = new_data.get('name')
		AccountLevelLocalId = new_data.get('accountLevel')
		AccountSectionLocalId = new_data.get('accountSection')
		TypeDate = new_data.get('typeDate')
		OtherTypeDate = new_data.get('otherTypeDate')
		NumberDayDuration = new_data.get('numberDayDuration')
		NumberSession = new_data.get('numberSession')
		TypeSession = new_data.get('typeSession')
		OtherTypeSession = new_data.get('otherTypeSession')
		ConditionOfPassage = new_data.get('conditionOfPassage')
		ConditionOfPassageFormule = new_data.get('conditionOfPassageFormule')
		ConditionOfPassageByNote = new_data.get('conditionOfPassageFormuleByNote')
		ConditionOfPassageFormuleByPresent = new_data.get('conditionOfPassageFormuleByPresent')
		ConditionOfPassageFormuleByNotePresent = new_data.get('conditionOfPassageFormuleByNotePresent')
		PublicResource = new_data.get('publicResource')
		Description = new_data.get('description')
		ImgLink = new_data.get('imgLink')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM account_level WHERE id = %s""",
			(AccountLevelLocalId,)
		)
		result = cursor.fetchone()
		accountLevelIdProd = result['id_prod']


		cursor.execute(
			"""SELECT id_prod FROM account_section WHERE id = %s""",
			(AccountSectionLocalId,)
		)
		result = cursor.fetchone()
		accountSectionIdProd = result['id_prod']


		payload = {
			"name":Name,
			"description": Description,
			"accountLevelId": accountLevelIdProd,
			"accountSectionId": accountSectionIdProd,
			"typeDate": TypeDate,
			"numberDayDuration": NumberDayDuration,
			"numberSession": NumberSession,
			"typeSession": TypeSession,

		}

		print(payload)

	except Exception as e:
		logger.exception("Error in push FormationAdd: %s", e)
		return False

def push_formationUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		FormationId = new_data.get('id')

		query = """
			SELECT id_prod
			FROM formation 
			WHERE id = %s
		"""
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(query, (FormationId,))
		result = cursor.fetchone()
		remote_formation_id = result['id_prod']
		if remote_formation_id is None:
			return False

		return _send_create_formation_api(settings, remote_formation_id)


	except Exception as e:
		logger.exception("Error in push_FormationUpdate: %s", FormationId)
		return False
	except Exception as e:
		logger.exception("Error in push_FormationUpdate: %s", e)
		return False

def push_formationDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		FormationId = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM formation WHERE id = %s""",
			(FormationId,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod']
		print(id_prod)
		status = _send_delete_formation_api(settings, id_prod)
		return status
	except Exception as e:
		logger.exception("Error in push_formationDelete: %s", FormationId)
		return False
