import sys
import os
import json
import logging
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Remote API calls
# ---------------------------------------------------------------------------

def _send_calendar_special_group(settings, payload):
    """Send special-group calendar to remote API."""
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-special-group-calendar"
        payload.pop('accountId', None)

        logger.debug("POST %s | payload: %s", url, payload)

        response = requests.post(url, data=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None, None, None

            relation_teacher_subject = response_data.get('newTeacherToSubjectGroupId')
            calendar_remote_id = response_data.get('calendarId')
            group_remote_id = response_data.get('newGroupSpecialId')
            logger.info(
                "Special group calendar created — calendarId=%s, newGroupSpecialId=%s, relationTeacherSubject=%s",
                calendar_remote_id, group_remote_id, relation_teacher_subject
            )
            return True, calendar_remote_id, group_remote_id, relation_teacher_subject

        elif response.status_code == 400:
            logger.error("Special API error 400: %s", response.text)
            return False, None, None, None

        else:
            logger.error("Unexpected status %s: %s", response.status_code, response.text)
            return False, None, None, None

    except requests.exceptions.Timeout:
        logger.error("Request timeout (10s) — %s", url)
        return False, None, None, None
    except Exception as e:
        logger.exception("Remote API error in _send_calendar_special_group: %s", e)
        return False, None, None, None


def _send_calendar(settings, payload):
    """Send normal-group calendar to remote API."""
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/create-calendar-normal-group"

        logger.debug("POST %s | payload: %s", url, payload)

        response = requests.post(url, data=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False, None

            remote_id = response_data.get('calendarId')
            logger.info("Normal group calendar created — calendarId=%s", remote_id)
            return True, remote_id

        else:
            logger.error("Remote API returned %s: %s", response.status_code, response.text)
            return False, None

    except requests.exceptions.Timeout:
        logger.error("Request timeout (10s) — %s", url)
        return False, None
    except Exception as e:
        logger.exception("Remote API error in _send_calendar: %s", e)
        return False, None


def _send_update_calander(settings, calendar_id, payload):
    """Send calendar update to remote API."""
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/edit-calendar/{calendar_id}"

        response = requests.post(url, data=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info("Calendar updated — %s", response_data)
                return True
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False
        else:
            logger.error("Remote API returned %s: %s", response.status_code, response.text)
            return False

    except Exception as e:
        logger.exception("Remote API error in _send_update_calander: %s", e)
        return False


def _send_delete_calander(settings, calendar_id, payload):
    """Send calendar delete to remote API."""
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/delete-calendar/{calendar_id}"

        response = requests.post(url, data=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info("Calendar deleted — %s", response_data)
                return True
            except Exception:
                logger.error("Invalid JSON response: %s", response.text)
                return False
        else:
            logger.error("Remote API returned %s: %s", response.status_code, response.text)
            return False

    except Exception as e:
        logger.exception("Remote API error in _send_delete_calander: %s", e)
        return False


# ---------------------------------------------------------------------------
# Push handlers (called by DataPusher)
# ---------------------------------------------------------------------------

def push_calendar_add(db, settings, row):
    """Handle calendar INSERT audit row."""
    try:
        new_data = json.loads(row.get('new_data', '{}'))
        group_id = new_data.get('group_id')
        local_calendar_id = row.get('id_calander')

        # Step 1: Check if group is special
        cursor_check = db.connection.cursor(dictionary=True)
        cursor_check.execute(
            "SELECT special_group FROM relation_group_local_session WHERE id = %s",
            (group_id,)
        )
        group = cursor_check.fetchone()
        cursor_check.close()

        is_special = group.get('special_group', False) if group else False
        logger.debug("Group %s is_special = %s", group_id, is_special)

        # Step 2: Extract date/time from new_data
        start_datetime = new_data.get('start_time', '')
        end_datetime = new_data.get('end_time', '')
        start_time = start_datetime.split(' ')[1][:5] if start_datetime else None
        end_time = end_datetime.split(' ')[1][:5] if end_datetime else None

        # Step 3: Build base payload
        payload = {
            'sessionId':    new_data.get('session_id'),
            'localId':      new_data.get('local_id'),
            'teacherId':    new_data.get('teacher_id'),
            'accountId':    new_data.get('account_id'),
            'startDate':    start_datetime.split(' ')[0] if start_datetime else None,
            'endDate':      '',
            'startTime':    start_time,
            'endTime':      end_time,
            'eventType':    'none',
            'typeSession':  new_data.get('type'),
            'eventTitle':   new_data.get('title'),
            'description':  new_data.get('description'),
            'completionTag': [],
        }

        if new_data.get('room_id'):
            payload['roomId'] = new_data.get('room_id')
        if new_data.get('subject_id'):
            payload['subjectId'] = new_data.get('subject_id')

        # Step 4: Route based on group type
        if is_special:
            logger.info("Group %s is SPECIAL — fetching extra fields from DB", group_id)

            cursor_extra = db.connection.cursor(dictionary=True)
            cursor_extra.execute(
                "SELECT capacity, access_type FROM relation_group_local_session WHERE id = %s",
                (group_id,)
            )
            extra = cursor_extra.fetchone()
            cursor_extra.close()

            if not extra:
                logger.error("Could not find extra fields for group #%s", group_id)
                return False

            payload['endDate']    = payload['startDate']
            payload['capacity']   = extra.get('capacity')
            payload['accessType'] = extra.get('access_type')
            payload['groupId']    = group_id

            result = _send_calendar_special_group(settings, payload)

            if result is None:
                logger.error("_send_calendar_special_group returned None")
                return False

            success, remote_calendar_id, remote_group_id, relation_teacher_subject = result

            if success and remote_calendar_id and remote_group_id:
                cursor_save = db.connection.cursor()

                cursor_save.execute(
                    "UPDATE relation_calander_group_session SET id_prod = %s WHERE id = %s",
                    (remote_calendar_id, local_calendar_id)
                )
                cursor_save.execute(
                    "UPDATE relation_group_local_session SET id_prod = %s WHERE id = %s",
                    (remote_group_id, group_id)
                )
                cursor_save.execute(
                    "UPDATE relation_teacher_to_subject_group SET id_prod = %s WHERE relation_group_local_session_id = %s",
                    (relation_teacher_subject, group_id)
                )

                db.connection.commit()
                cursor_save.close()

                logger.info(
                    "Saved remote_calendar_id=%s → relation_calander_group_session #%s",
                    remote_calendar_id, local_calendar_id
                )
                logger.info(
                    "Saved remote_group_id=%s → relation_group_local_session #%s",
                    remote_group_id, group_id
                )

            elif not success:
                logger.warning("Marking calendar #%s as is_synced=2 (failed)", local_calendar_id)
                cursor_save = db.connection.cursor()
                cursor_save.execute(
                    "UPDATE relation_calander_group_audit SET is_synced = 2 WHERE id_calander = %s",
                    (local_calendar_id,)
                )
                db.connection.commit()
                cursor_save.close()

        else:
            logger.info("Group %s is NORMAL — using standard API", group_id)
            payload['groupId'] = new_data.get('group_id')

            logger.debug("Normal group payload: %s", payload)
            success, remote_calendar_id = _send_calendar(settings, payload)

            if success and remote_calendar_id:
                cursor_save = db.connection.cursor()
                cursor_save.execute(
                    "UPDATE relation_calander_group_session SET id_prod = %s WHERE id = %s",
                    (remote_calendar_id, local_calendar_id)
                )
                db.connection.commit()
                cursor_save.close()

                logger.info(
                    "Saved remote_calendar_id=%s → relation_calander_group_session #%s",
                    remote_calendar_id, local_calendar_id
                )

        return success

    except Exception as e:
        logger.exception("Error in push_calendar_add: %s", e)
        return False


def push_calendar_update(db, settings, row):
    """Handle calendar UPDATE audit row."""
    try:
        calendar_id = row.get('calendar_id')
        payload = {
            'calendar_date': row.get('calendar_date'),
            'start_time':    row.get('start_time'),
            'end_time':      row.get('end_time'),
        }
        return _send_update_calander(settings, calendar_id, payload)
    except Exception as e:
        logger.exception("Error in push_calendar_update: %s", e)
        return False


def push_calendar_delete(db, settings, row):
    """Handle calendar DELETE audit row."""
    try:
        calendar_id = row.get('calendar_id')
        return _send_delete_calander(settings, calendar_id, {})
    except Exception as e:
        logger.exception("Error in push_calendar_delete: %s", e)
        return False