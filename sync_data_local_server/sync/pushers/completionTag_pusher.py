import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


logger = logging.getLogger(__name__)

def _send_create_completionTag_api(settings, payload):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-completion-tag-account"

        logger.debug("POST %s | payload: %s", url, payload)

        response = requests.post(url, data=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
            completionTagId = response_data.get('id')
            logger.info("CompletionTag created")
            return True, completionTagId
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
        logger.exception("Remote API error in create CompletionTag: %s", e)
        return False, None

def _send_update_completionTag_api(settings, payload, completionTag):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/update-completion-tag-account/{completionTag}"
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info("AccountSubject updated  - %s", response_data)
                return True
            except Exception:
                logger.error("Invalid JSON  response: %s", response.text)
                return False
        else:
            logger.error("Remote API returned %s: %s", response.status_code, response.text)
            return False
    except Exception as e:
        logger.exception("Remote API error in _send_update_completion_tag: %s",e)
        return False
    except Exception as e:
        logger.exception("Remote API error in _send_update_completionTag: %s", e)
        return False

def _send_delete_completionTag_api(settings,completionTagId):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/delete-completion-tag-account/{completionTagId}"

        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info("CompletionTag deleted - %s", response_data)
                return True
            except Exception:
                logger.error("Invalid JSON reponse: %s",response.text)
                return False
        else:
            logger.error("Remote API returned %s: %s", response.status_code,response.text)
            return False
    except Exception as e:
        logger.exception("Remote API error in _send_delete_completionTag_api: %s",e)
        return False



def push_completionTagAdd(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data', '{}'))
        Name= new_data.get('name')
        Description = new_data.get('description') or None
        CompletionTagIdLocal = new_data.get('id')
        payload = {
            "name": Name,
            "description": Description
        }
        status,CompletionTagId = _send_create_completionTag_api(settings, payload)
        if status and CompletionTagId:
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute(
                """UPDATE completion_tag_account set id_prod =%s WHERE id = %s""",
                (CompletionTagId, CompletionTagIdLocal)
            )
            db.connection.commit()
            cursor.close()
            logger.info("CompletionTag updated <UNK> %s", CompletionTagIdLocal)

        return status
    except Exception as e:
        logger.exception("Error in push CompletionTagAdd: %s", e)
        return False

def push_completionTagUpdate(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data','{}'))
        CompletionTagId = new_data.get('id')
        Name = new_data.get('name')
        Description = new_data.get('description') or None
        Status = new_data.get('status')
        payload = {
            "name": Name,
            "description": Description
        }
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_prod FROM completion_tag_account WHERE id = %s""",
            (CompletionTagId,)
        )
        result = cursor.fetchone()
        id_prod = result['id_prod']
        success = _send_update_completionTag_api(settings,payload,id_prod)
        return success
    except Exception as e:
        logger.exceptin("Error in push_CompletionTagUpdate: %s", CompletionTagId)
        return False
    except Exception as e:
        logger.exception("Error in push_accountCompletionTagUpdate: %s", e)
        return False

def push_completionTagDelete(db, settings, row):
    try:
        old_data = json.loads(row.get('old_data', '{}'))
        CompletionTag = old_data.get('id')
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_prod FROM completion_tag_account WHERE id = %s""",
            (CompletionTag,)
        )
        result = cursor.fetchone()
        id_prod = result['id_prod']
        status= _send_delete_completionTag_api(settings,id_prod)
        return status
    except Exception as e:
        logger.exception("Error in push_completionTagDelete: %s", CompletionTag)
        return False