import logging
import os
import sys
import json
import requests
from core.auth import get_token
import mimetypes

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)



def _send_create_session_api(settings, payload, img_link=None):
    image_fp = None
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-session"

        files = {}
        if img_link:
            uploads_path = "../server_local_api/uploads"  # sync_data_local_server -> server_local_api
            local_path = os.path.join(uploads_path, img_link)

            logger.debug("Resolved session image path: %s | exists: %s", local_path, os.path.exists(local_path))
            if os.path.exists(local_path):
                mime_type, _ = mimetypes.guess_type(local_path)
                image_fp = open(local_path, "rb")
                files["image"] = (os.path.basename(local_path), image_fp, mime_type or "application/octet-stream")
            else:
                logger.warning("Session image not found on disk: %s", local_path)

        logger.debug("POST %s | payload: %s | files: %s", url, payload, list(files.keys()))

        response = requests.post(
            url, data=payload, files=files if files else None,
            headers=headers, verify=False, timeout=10
        )

        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
            sessionID = response_data.get('data', {}).get('id')
            return True, sessionID
        elif response.status_code == 400:
            logger.error("Invalid JSON response: %s", response.text)
            return False, None
        else:
            logger.error("Unexpected status %s: %s", response.status_code, response.text)
            return False, None

    except Exception as e:
        logger.exception("Remote API error in create session: %s", e)
        return False, None

    finally:
        if image_fp:
            image_fp.close()

def _send_delete_session_api(settings, session_id):
    url = f"{settings.api_base_url}/slc/delete-session/{session_id}"
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(url, headers=headers, timeout=10)
        print(response.status_code)
        if response.status_code == 200:
            return True
        else:
            print(f"_send_delete_session_api: unexpected status {response.status_code} for session_id={session_id}, body={response.text}")
            return False
    except Exception as e:
        print(f"Error: {e} in _send_delete_session_api for session_id={session_id}")
        return False

def _send_update_session_api(settings, session_id, payload, img_link=None):
    image_fp = None
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/update-session/{session_id}"

        files = {}
        if img_link:
            uploads_path = "../server_local_api/uploads"  # sync_data_local_server -> server_local_api
            local_path = os.path.join(uploads_path, img_link)

            logger.debug("Resolved session image path: %s | exists: %s", local_path, os.path.exists(local_path))
            if os.path.exists(local_path):
                mime_type, _ = mimetypes.guess_type(local_path)
                image_fp = open(local_path, "rb")
                files["image"] = (os.path.basename(local_path), image_fp, mime_type or "application/octet-stream")
            else:
                logger.warning("Session image not found on disk: %s", local_path)

        logger.debug("PUT %s | payload: %s | files: %s", url, payload, list(files.keys()))

        response = requests.post(
            url, data=payload, files=files if files else None,
            headers=headers, verify=False, timeout=10
        )

        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None
            sessionID = response_data.get('data', {}).get('id')
            return True, sessionID
        elif response.status_code == 400:
            logger.error("Invalid JSON response: %s", response.text)
            return False, None
        else:
            logger.error("Unexpected status %s | body: %.500s", response.status_code, response.text)
            return False, None

    except Exception as e:
        logger.exception("Remote API error in update session: %s", e)
        return False, None

    finally:
        if image_fp:
            image_fp.close()

def push_sessionAdd(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data', '{}'))

        extra_data = new_data.get('extra_data') or []
        has_extra_session = len(extra_data) > 0

        # extra_data must land as parallel arrays under these exact keys,
        # since the Symfony endpoint zips them by index:
        #   extra_data_name[i], extra_data_type[i], extra_data_required[i],
        #   extra_data_example[i], extra_data_description[i]
        extra_data_name = []
        extra_data_type = []
        extra_data_required = []
        extra_data_example = []
        extra_data_description = []

        for item in extra_data:
            extra_data_name.append(item.get('field_name', ''))
            extra_data_type.append(item.get('type', ''))
            extra_data_required.append(item.get('required', ''))
            extra_data_example.append(item.get('example', ''))
            extra_data_description.append(item.get('description', ''))

        # Build payload as a LIST OF TUPLES, not a dict — a dict can't hold
        # duplicate keys, and form-encoding needs each extra_data_* array
        # sent as repeated "key[]" entries for PHP to parse them as arrays.
        payload = [
            ("name", new_data.get('name')),
            ("description", new_data.get('description')),
            ("start_date", new_data.get('start_date')),
            ("end_date", new_data.get('end_date')),
            ("capacity", new_data.get('capacity')),
            ("price", new_data.get('price')),
            ("currency", new_data.get('currency')),
            ("type_pay", new_data.get('type_pay')),
            ("payment_method", new_data.get('payment_methode')),
            ("number_session_for_pay", new_data.get('number_session_for_pay')),
            ("price_student_absent", new_data.get('price_student_absent')),
            ("user_register_after_start", new_data.get('user_register_after_start')),
            ("special_group", new_data.get('special_group')),
            ("request_change_group", new_data.get('request_change_group')),
            ("max_group_change", new_data.get('max_group_change')),
            ("payment_deadline", new_data.get('payment_deadline')),
            ("formation_id", new_data.get('formation_id')),
            ("season_id", new_data.get('season_id') or None),
            ("extra_session", has_extra_session),
        ]

        # Drop None values (requests will skip them anyway, but keeps it clean)
        payload = [(k, v) for k, v in payload if v is not None]

        # extra_data_* must always be present as arrays, even if empty,
        # since Symfony reads them unconditionally with no ?? [] fallback.
        if has_extra_session:
            for i in range(len(extra_data_name)):
                payload.append(("extra_data_name[]", extra_data_name[i]))
                payload.append(("extra_data_type[]", extra_data_type[i]))
                payload.append(("extra_data_required[]", extra_data_required[i]))
                payload.append(("extra_data_example[]", extra_data_example[i]))
                payload.append(("extra_data_description[]", extra_data_description[i]))
        else:
            payload.append(("extra_data_name[]", ""))
            payload.append(("extra_data_type[]", ""))
            payload.append(("extra_data_required[]", ""))
            payload.append(("extra_data_example[]", ""))
            payload.append(("extra_data_description[]", ""))

        status, session_id_prod = _send_create_session_api(settings, payload, img_link=new_data.get('img_link'))

        if status and session_id_prod:
            id_local = row.get('id_session') or new_data.get('id')
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("""
                UPDATE session SET id_prod = %s WHERE id = %s
            """, (session_id_prod, id_local))
            db.connection.commit()
            cursor.close()
            logger.info("Session updated id_prod=%s for local id=%s", session_id_prod, id_local)

        return status

    except Exception as e:
        print(f"❌ Error in push_sessionAdd: {e}")
        return False

def push_sessionDelete(db, settings, row):
    try:
        data = json.loads(row.get('old_data', '{}'))
        idLocal = data.get('id')
        id_prod = data.get('id_prod')  # prefer the snapshot value if present

        if not id_prod:
            # fallback: try local DB in case the row still exists
            idProd = db.fetch_query("""SELECT id_prod FROM session WHERE id=%s""", (idLocal,))
            id_prod = idProd[0][0] if idProd else None

        if not id_prod:
            print(f"push_sessionDelete: no id_prod found for local id={idLocal}")
            return False

        return _send_delete_session_api(settings, id_prod)
    except Exception as e:
        print(f"Error: {e} in push_sessionDelete")
        return False

def push_sessionUpdate(db, settings, row):
    try:
        new_data = json.loads(row.get('new_data', '{}'))
        SessionIdLocal = new_data.get('id')
        Name = new_data.get('name')
        FormationIdLocal = new_data.get('formation_id')
        Capacity = new_data.get('capacity')
        TypePay = new_data.get('type_pay')
        ImgLink = new_data.get('img_link')

        # --- resolve remote session id (id_prod) BEFORE building payload ---
        session_rows = db.fetch_query(
            "SELECT id_prod FROM session WHERE id = %s",
            (SessionIdLocal,)
        )
        if not session_rows or not session_rows[0].get('id_prod'):
            print(f"push_sessionUpdate: no id_prod found for local session {SessionIdLocal}")
            return False
        SessionProdId = session_rows[0]['id_prod']

        # --- resolve remote formation id (id_prod) BEFORE building payload ---
        formation_rows = db.fetch_query(
            "SELECT id_prod FROM formation WHERE id = %s",
            (FormationIdLocal,)
        )
        if not formation_rows or not formation_rows[0].get('id_prod'):
            print(f"push_sessionUpdate: no id_prod found for local formation {FormationIdLocal}")
            return False
        FormationProdId = formation_rows[0]['id_prod']

        payload = {
            "name": new_data.get('name'),
            "description": new_data.get('description'),
            "start_date": new_data.get('start_date'),
            "end_date": new_data.get('end_date'),
            "capacity": new_data.get('capacity'),
            "price": new_data.get('price'),
            "currency": new_data.get('currency'),
            "type_pay": new_data.get('type_pay'),
            "payment_method": new_data.get('payment_method'),
            "number_session_for_pay": new_data.get('number_session_for_pay'),
            "price_student_absent": new_data.get('price_student_absent'),
            "user_register_after_start": new_data.get('user_register_after_start'),
            "special_group": new_data.get('special_group'),
            "request_change_group": new_data.get('request_change_group'),
            "max_group_change": new_data.get('max_group_change'),
            "payment_deadline": new_data.get('payment_deadline'),
            "formation_id": FormationProdId,
            "extra_session": new_data.get('extra_session'),
        }

        success, sessionID = _send_update_session_api(settings, SessionProdId, payload, img_link=ImgLink)
        if not success:
            print(f"push_sessionUpdate: failed to update session {SessionProdId}")
            return False

        return True

    except Exception as e:
        print(f"Error: {e} coming from push_sessionUpdate")
        return False