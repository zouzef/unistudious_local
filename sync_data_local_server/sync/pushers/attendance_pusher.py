import sys
import os
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.auth import get_token

# API unistudious add student to attendance
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

# API unistudious update note attendance
def _send_note_update(settings,attendance_id,note):
    try:
        token = get_token()

        headers = {"Authorization": f"Bearer {token}"}
        payload = {'note':str(note)}
        print("payload:",payload)
        url = f"{settings.api_base_url}/slc/update-attendance-note/{attendance_id}"
        print(url)
        response = requests.post(url,data=payload,headers=headers,timeout=10)
        if response.status_code == 200:
            print("hiii")
            response_data = response.json()
            print(f"✅ Remote API success: {response_data}")
            return True
        else:
            print(f"❌ Remote API returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending request: {e}")
        return False

# API unistudious update status attendance
def _update_status_attendance(settings, attendance_id,is_present):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"status":is_present}
        url = f"{settings.api_base_url}/slc/update-attendance-student/{attendance_id}"
        response = requests.post(url,data=payload,headers=headers,timeout=10)

        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Remote API success: {response_data}")
            return True
    except Exception as e:
        return False




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
        print(attendance_data)


        return True

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing new_data JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in push_add: {e}")
        import traceback
        traceback.print_exc()
        return False


def push_update(db, settings, audit_row):
    print("🔄 UPDATE — pushing changes to remote...")

    try:
        old_data = audit_row.get('old_data')
        new_data = audit_row.get('new_data')
        id_attendance = audit_row.get('id_attendance')

        if not old_data or not new_data:
            print("⏭️ Skipping - missing old or new data")
            return False

        old_relation = json.loads(old_data)
        new_relation = json.loads(new_data)

        # Get id_prod from attendance table
        conn = db.connection
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_prod FROM attendance WHERE id = %s
        """, (id_attendance,))
        row = cursor.fetchone()
        cursor.close()

        if not row or not row['id_prod']:
            print(f"❌ No id_prod found for local attendance id={id_attendance} — skipping")
            return False

        id_prod = row['id_prod']
        print(f"🔗 id_prod = {id_prod}")

        success = True

        # Check if is_present changed
        old_is_present = old_relation.get('is_present')
        new_is_present = new_relation.get('is_present')

        if old_is_present != new_is_present:
            print(f"🎯 is_present changed: {old_is_present} → {new_is_present}")
            result = _update_status_attendance(settings, id_prod, new_is_present)
            if not result:
                print("❌ Failed to update is_present")
                success = False
            else:
                print("✅ is_present updated successfully")

        # Check if note changed
        old_note = old_relation.get('note')
        new_note = new_relation.get('note')

        if old_note != new_note:
            print(f"🎯 note changed: {old_note} → {new_note}")
            print("\n \n \n ",new_note)
            result = _send_note_update(settings, id_prod, new_note)
            if not result:
                print("❌ Failed to update note")
                success = False
            else:
                print("✅ note updated successfully")

        # No changes detected
        if old_is_present == new_is_present and old_note == new_note:
            print("⏭️ No meaningful changes detected — skipping")
            return True

        return success

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in push_update: {e}")
        import traceback
        traceback.print_exc()
        return False