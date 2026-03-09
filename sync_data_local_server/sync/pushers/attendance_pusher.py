import sys
import os
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.auth import get_token


def _send_attendance_request(settings, payload):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/attendance-save-user"

        print(f"📡 Sending to remote: {url}")
        print(f"📦 Payload: {payload}")

        response = requests.post(url, data=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Remote API success: {response_data}")
            remote_id = response_data.get('attendance', {}).get('id')
            return True, remote_id
        else:
            print(f"❌ Remote API returned {response.status_code}: {response.text}")
            return False, None

    except Exception as e:
        print(f"❌ Error sending request: {e}")
        return False, None


def _find_calendar_id(db, user_id, session_id):
    try:
        conn = db.connection
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.calander_id 
            FROM attendance a
            WHERE a.user_id = %s AND a.session_id = %s
            AND a.enabled = 1
            LIMIT 1
        """, (user_id, session_id))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return row['calander_id']
        return None

    except Exception as e:
        print(f"❌ Error finding calendar_id: {e}")
        return None


def push_add(db, settings, audit_row):
    print("🎓 ADD_STUDENT — pushing to remote...")

    try:
        new_data = audit_row.get('new_data')
        id_attendance = audit_row.get('id_attendance')

        if not new_data:
            print("❌ No new_data in audit row — skipping")
            return False

        attendance_data = json.loads(new_data)

        user_id = attendance_data.get('userId')
        calendar_id = attendance_data.get('calendarId')
        group_id = attendance_data.get('groupId')
        relation_id = attendance_data.get('relationId')
        add_to_group = attendance_data.get('addToGroup')
        selected_group_id = attendance_data.get('selectedGroupId')
        join_to_group = attendance_data.get('joinToGroup')

        if not user_id or not calendar_id:
            print("❌ Missing userId or calendarId — skipping")
            return False

        print(f"👤 User ID: {user_id}")
        print(f"📅 Calendar ID: {calendar_id}")
        print(f"👥 Group ID: {group_id}")

        payload = {
            "userId": user_id,
            "calendarId": calendar_id,
            "groupId": group_id,
            "relationId": relation_id,
            "addToGroup": add_to_group,
            "selectedGroupId": selected_group_id,
            "joinToGroup": join_to_group
        }

        success, remote_id = _send_attendance_request(settings, payload)

        if success and remote_id:
            conn = db.connection
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE attendance 
                SET id_prod = %s 
                WHERE id = %s
            """, (remote_id, id_attendance))
            conn.commit()
            cursor.close()
            print(f"✅ id_prod={remote_id} saved for local attendance id={id_attendance}")
        elif success and not remote_id:
            print("⚠️ Remote returned no attendance id — id_prod not updated")

        return success

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing new_data JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in push_add: {e}")
        import traceback
        traceback.print_exc()
        return False


def push_update(db, settings, audit_row):
    print("🔄 UPDATE — pushing group change to remote...")

    try:
        old_data = audit_row.get('old_data')
        new_data = audit_row.get('new_data')

        if not old_data or not new_data:
            print("⏭️ Skipping - missing old or new data")
            return False

        old_relation = json.loads(old_data)
        new_relation = json.loads(new_data)

        old_group_id = old_relation.get('relation_group_local_session_id')
        new_group_id = new_relation.get('relation_group_local_session_id')
        user_id = new_relation.get('user_id')
        session_id = new_relation.get('session_id')
        relation_id = new_relation.get('id')

        print(f"🔄 Group change: {old_group_id} -> {new_group_id}")
        print(f"👤 User ID: {user_id}")
        print(f"📅 Session ID: {session_id}")
        print(f"🔗 Relation ID: {relation_id}")

        if not user_id or not session_id:
            print("❌ Missing user_id or session_id — skipping")
            return False

        calendar_id = _find_calendar_id(db, user_id, session_id)
        if not calendar_id:
            print("❌ Could not find calendar_id — skipping")
            return False

        if old_group_id is None and new_group_id is not None:
            print("🎯 SCENARIO: Student joining a group")
            payload = {
                "userId": user_id,
                "calendarId": calendar_id,
                "groupId": new_group_id,
                "relationId": relation_id,
                "addToGroup": False,
                "selectedGroupId": None,
                "joinToGroup": True
            }

        elif old_group_id and new_group_id and old_group_id != new_group_id:
            print("🎯 SCENARIO: Student moving between groups")
            payload = {
                "userId": user_id,
                "calendarId": calendar_id,
                "groupId": new_group_id,
                "relationId": relation_id,
                "addToGroup": True,
                "selectedGroupId": old_group_id,
                "joinToGroup": False
            }

        else:
            print("⏭️ No meaningful group change detected — skipping")
            return True

        success, _ = _send_attendance_request(settings, payload)
        return success

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in push_update: {e}")
        import traceback
        traceback.print_exc()
        return False