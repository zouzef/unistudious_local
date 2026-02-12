from flask import Blueprint, jsonify, request
from datetime import datetime,timedelta
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from core.database import Database
from core.middleware import token_required
import random
import string
import requests
import json

# Create blueprint
calendar_bp = Blueprint('calendar', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Delete calendar interval
# ========================================
@calendar_bp.route('/deleting_interval/<int:session_id>', methods=['POST'])
# @token_required
def delete_calendar(session_id):
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400

        start_date_str = data.get('start_date')
        print("start_date", start_date_str)

        end_date_str = data.get('end_date')
        print("end_date", end_date_str)

        # Validate
        if not start_date_str or not end_date_str:
            return jsonify({"message": "Missing start_date or end_date"}), 400

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        # Find calendars in the interval
        query = """
            SELECT id FROM relation_calander_group_session
            WHERE start_time <= %s AND end_time >= %s
        """
        results = Database.execute_query(query, (end_date_str, start_date_str))

        if results:
            ids = [row['id'] for row in results]
            placeholders = ','.join(['%s'] * len(ids))

            # Soft delete by setting enabled = 0
            query = f"""
                UPDATE relation_calander_group_session 
                SET enabled = 0 
                WHERE id IN ({placeholders})
            """
            Database.execute_query(query, ids, fetch=False)

            return jsonify({"message": "success", "data": results}), 200
        else:
            return jsonify({"message": "There is no session"}), 400

    except Exception as e:
        print(f"Error {e} coming from deleting function !!")
        return jsonify({"message": f"Error: {str(e)}"}), 500

# ========================================
# ENDPOINT 2: Get calendar by ID
# ========================================
@calendar_bp.route('/get_calander_id/<int:id_calender>', methods=['GET'])
# @token_required
def get_calendar_by_id(id_calender):
    try:
        query = """
            SELECT * FROM relation_calander_group_session 
            WHERE id = %s AND enabled = 1
        """
        result = Database.execute_query(query, (id_calender,))

        if result:
            return jsonify({"message": "Success", "data": result[0]}), 200
        else:
            return jsonify({"message": f"Calendar not found for {id_calender}"}), 404

    except Exception as e:
        print(f"DEBUG: error {e}")
        return jsonify({"message": "Error"}), 500


# ========================================
# ENDPOINT 3: Get group from calendar
# ========================================
@calendar_bp.route('/get-group-calender/<int:calendarId>', methods=["GET"])
def get_group_calendar(calendarId):
    try:
        query = """
            SELECT group_session_id FROM relation_calander_group_session 
            WHERE id = %s LIMIT 1
        """
        calendar = Database.execute_query(query, (calendarId,))

        if not calendar:
            return jsonify({"error": "calendar not found"}), 404

        group_id = calendar[0]['group_session_id']

        return jsonify({"group_session_id": group_id}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 4: Get next session
# ========================================
@calendar_bp.route('/get_next_session/<int:calendarId>', methods=["GET"])
def get_next_session(calendarId):
    try:
        # Get the current calendar's start time
        query = """
            SELECT start_time FROM relation_calander_group_session 
            WHERE id = %s
        """
        selected_time = Database.execute_query(query, (calendarId,))

        if not selected_time:
            return jsonify({"error": "Calendar not found"}), 404

        print(selected_time)

        # Get the next session after this time
        query = """
            SELECT start_time, id 
            FROM relation_calander_group_session 
            WHERE start_time > %s 
            ORDER BY start_time ASC
            LIMIT 1
        """
        next_session = Database.execute_query(query, (selected_time[0]["start_time"],))

        if next_session:
            return jsonify({"data": next_session[0]}), 200
        else:
            return jsonify({"data": None, "message": "No next session found"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 5: Get all today's calendars
# ========================================
@calendar_bp.route('/get-all-calender', methods=['GET'])
def get_todays_sessions():
    try:
        query = """
            SELECT 
                r.id,
                r.title AS name,
                r.start_time AS start,
                r.end_time AS end,
                r.teacher_id AS teacherId,
                u.uuid AS teacherUuid,
                u.full_name AS teacherFullName,
                r.subject_id AS subjectId,
                CASE
                    WHEN sc.id != 1 THEN sc.name 
                    ELSE acs.other_subject
                END AS subjectName,
                r.local_id AS localId,
                l.name AS localName,
                r.room_id AS roomId,
                rm.name AS roomName,
                r.session_id AS sessionId,
                s.name AS sessionName,
                r.description AS description
            FROM relation_calander_group_session r
            LEFT JOIN user u ON r.teacher_id = u.id
            LEFT JOIN local l ON r.local_id = l.id
            LEFT JOIN relation_teacher_to_subject_group rtsg ON r.subject_id = rtsg.id
            LEFT JOIN subject_config sc ON rtsg.subject_id = sc.id
            LEFT JOIN room rm ON r.room_id = rm.id
            LEFT JOIN account_subject acs ON acs.subject_config_id = sc.id
            LEFT JOIN session s ON r.session_id = s.id
            WHERE r.enabled = 1
        """
        rows = Database.execute_query(query)

        now = datetime.utcnow()
        today = now.date()
        filtered_rows = []

        for row in rows:
            start_time_dt = row.get("start")

            if isinstance(start_time_dt, str):
                start_time_dt = datetime.fromisoformat(start_time_dt)

            if start_time_dt and start_time_dt.date() == today:
                end_time_dt = row.get("end")
                if isinstance(end_time_dt, str):
                    end_time_dt = datetime.fromisoformat(end_time_dt)

                if end_time_dt and now <= end_time_dt + timedelta(minutes=5):
                    filtered_rows.append(row)

        filtered_rows.sort(key=lambda x: x["start"])

        return jsonify({"data": filtered_rows}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 6: Get account data by calendar
# ========================================
@calendar_bp.route('/data_account/<int:id>', methods=['GET'])
def data_account_api(id):
    try:
        query = """
            SELECT a.*
            FROM account a 
            JOIN relation_calander_group_session rcg ON rcg.id = %s
            WHERE rcg.account_id = a.id
        """
        rows = Database.execute_query(query, (id,))

        print(rows)
        return jsonify({"status": "ok", "data": rows}), 200

    except Exception as e:
        print("ERROR IN data_account:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ========================================
# ENDPOINT 7: Get calendar by session and account
# ========================================
@calendar_bp.route('/get_calendar_session/<int:id_session>/<int:id_account>', methods=['GET'])
def get_calendar_session(id_session, id_account):
    try:
        print(id_session)
        print(id_account)
        query = """
            SELECT * FROM relation_calander_group_session 
            WHERE enabled = 1 AND session_id = %s AND account_id = %s
        """
        result = Database.execute_query(query, (id_session, id_account))

        if result:
            # Convert datetime objects to Tunisia timezone (UTC+1)
            timezone_offset = timedelta(hours=1)

            for event in result:
                # Convert start_time if it exists and is a datetime object
                if event.get('start_time') and isinstance(event['start_time'], datetime):
                    event['start_time'] = event['start_time'] + timezone_offset
                    event['start_time'] = event['start_time'].isoformat()

                # Convert end_time if it exists and is a datetime object
                if event.get('end_time') and isinstance(event['end_time'], datetime):
                    event['end_time'] = event['end_time'] + timezone_offset
                    event['end_time'] = event['end_time'].isoformat()

                # Convert other datetime fields if needed
                if event.get('created_at') and isinstance(event['created_at'], datetime):
                    event['created_at'] = (event['created_at'] + timezone_offset).isoformat()

                if event.get('updated_at') and isinstance(event['updated_at'], datetime):
                    event['updated_at'] = (event['updated_at'] + timezone_offset).isoformat()

                if event.get('timestamp') and isinstance(event['timestamp'], datetime):
                    event['timestamp'] = (event['timestamp'] + timezone_offset).isoformat()

            return jsonify({"message": "Success", "data": result}), 200
        else:
            return jsonify({"message": f"Calendar not found for {id_session}/{id_account}"}), 404

    except Exception as e:
        print(f"Debug Error {e}")
        return jsonify({"message": "Error from server"}), 500


#================ create calender part ==============

# Generate color random for the calander
def generate_random_color():
    return f'#{random.randint(0,0xFFFFFF):06X}'

# Generate ref id for the calendar+
def generate_unique_ref(group_id,session_id,local_id,account_id):
    prefix = "group-"
    suffix = ''.join(random.choices(string.digits,k=3))
    return f"{prefix}{group_id}{session_id}{local_id}{account_id}-{suffix}"


# Function to test if the room reserved or no
def isRoomReserved(room_id, start_time, end_time):
    try:
        query = """
            SELECT COUNT(*) as nbr FROM relation_calander_group_session 
            WHERE room_id = %s 
            AND DATE(start_time) = DATE(%s)
            AND start_time < %s 
            AND end_time > %s
            AND enabled = 1 
        """
        values = (room_id, start_time, end_time, start_time)

        result = Database.execute_query(query,values)
        if result and len(result) > 0 :
            return result[0]['nbr'] > 0  # FIXED

    except Exception as db_error:
        print(f"Database Error: {db_error}")
        return True


# Check if the group is alreay in the time or no
def isGroupTypeConflit(group_id, start_time, end_time):
    try:
        query = """
            SELECT COUNT(*) as nbr FROM relation_calander_group_session 
            WHERE group_session_id = %s 
            AND DATE(start_time) = DATE(%s)
            AND start_time < %s
            AND end_time > %s
            AND enabled = 1
        """
        values = (group_id, start_time, end_time, start_time)

        result = Database.execute_query(query,values)
        if result and len(result)>0:
            return result[0]['nbr']>0
    except Exception as e:
        print(f"Database Error: {e}")
        return True


# Check if the subject and the teacher is on the time or no
def isSubjectTeacherConflit(teacher_id, start_time, end_time):
    try:
        query = """
            SELECT COUNT(*) AS nbr FROM relation_calander_group_session
            WHERE enabled = 1 
            AND teacher_id = %s
            AND DATE(start_time) = DATE(%s)
            AND start_time < %s
            AND end_time > %s 
        """
        values = (teacher_id, start_time, end_time, start_time)


        result = Database.execute_query(query,values)
        if result and len(result)>0:
            return result[0]['nbr']>0
    except Exception as e:
        print(f"Database Error: {e}")
        return True


# Check if the color generated or no
def check_color(color):
    try:
        query = """
            SELECT COUNT(*) AS nbr FROM relation_calander_group_session
            WHERE color = %s AND enabled = 1
        """
        values = (color,)

        result = Database.execute_query(query,values)
        if result and len(result)>0:
            return result[0]['nbr'] > 0  # FIXED

    except Exception as e:
        print(f"Database Error: {e}")
        return True

# ========================================
# ENDPOINT 8: Create calendar api
# ========================================
# Create calendar api 
@calendar_bp.route('/create_calender',methods=['POST'])
def create_calander():
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"Message": "No data from the request"}), 400

        # Required fields
        required_keys = [
            'session_id', 'account_id', 'local_id', 'group_id',
            'room_id', 'teacher_id', 'subject_id', 'description',
            'start_time', 'end_time', 'title', 'type'
        ]

        # Check for missing fields
        missing_fields = [key for key in required_keys if key not in data]
        if missing_fields:
            return jsonify({
                "Message": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        # Check for empty values
        empty_fields = []
        for key in required_keys:
            value = data[key]
            if value is None:
                empty_fields.append(key)
            elif isinstance(value, str) and value.strip() == "":
                empty_fields.append(key)

        if empty_fields:
            return jsonify({
                "Message": "Fields cannot be empty",
                "empty_fields": empty_fields
            }), 400

        # Extract values
        session_id = data['session_id']
        account_id = data['account_id']
        local_id = data['local_id']
        group_id = data['group_id']
        room_id = data['room_id']
        teacher_id = data['teacher_id']
        subject_id = data['subject_id']
        description = data['description']
        start_time = data['start_time']
        end_time = data['end_time']
        title = data['title']
        type_val = data['type']

        # Conflict checks
        if isRoomReserved(room_id, start_time, end_time):
            return jsonify({
                "Message": "Room already reserved!",
                "Error": "Room-Conflict",
            }), 402

        if isGroupTypeConflit(group_id, start_time, end_time):
            return jsonify({
                "Message": "Group not available in this time",
                "Error": "Group-Conflict"
            }), 402

        if isSubjectTeacherConflit(teacher_id, start_time, end_time):
            return jsonify({
                "Message": "Teacher not available in this time",
                "Error": "Teacher-Conflict"
            }), 402

        # Generate unique color
        color = generate_random_color()
        attempts = 0
        max_attempts = 50
        while check_color(color) and attempts < max_attempts:
            color = generate_random_color()
            attempts += 1

        if attempts >= max_attempts:
            return jsonify({
                "Message": "Could not find unique color",
                "Error": "Warning: Could not find unique color after 50 attempts"
            }), 402

        # Generate additional fields
        status = 1
        ref = generate_unique_ref(group_id, session_id, local_id, account_id)
        enabled = 1
        create_time = datetime.now()
        timestamp = create_time
        teacher_present = 0
        force_teacher_present = 0

        query = """
            INSERT INTO relation_calander_group_session
            (session_id, account_id, local_id, group_session_id, room_id, teacher_id, subject_id, color, status, description, start_time, end_time, ref, refresh, title, enabled, created_at, timestamp, updated_at, type, teacher_present, force_teacher_present, slc_use)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """


        values = (
            session_id,
            account_id,
            local_id,
            group_id,
            room_id,
            teacher_id,
            subject_id,
            color,
            status,
            description,
            start_time,
            end_time,
            ref,
            0,
            title,
            enabled,
            create_time,
            timestamp,
            None,
            type_val,
            teacher_present,
            force_teacher_present,
            1
        )

        # Execute insert query using Database helper
        calander_id = Database.execute_query(query, values, fetch=False)

        return jsonify({
            "Message": "Calendar entry created successfully",
            "calander_id": calander_id,
            "ref": ref,
            "color": color
        }), 201

    except Exception as e:
        print(f"Error from Server: {e}")
        return jsonify({
            "Message": "Internal Server Error",
            "error": str(e)
        }), 500


# =======================================
# ENDPOINT 9: Create subject_account api
#========================================

@calendar_bp.route('/get-subject-account/<int:account_id>',methods=['GET'])
def get_subject_account(account_id):
    try:
        query = """
            SELECT * from account_subject
            WHERE account_id = %s AND enabled = 1
        """

        values = (account_id,)
        subjects = Database.execute_query(query, values)

        seen_subjects = set()
        result = []

        for subject in subjects:
            subject_name = None

            if subject.get('other_subject') and subject['other_subject'].strip() != '':
                subject_name = subject['other_subject']
            else:
                config_query = """
                    SELECT name FROM subject_config
                    WHERE id = %s AND enabled = 1 
                """
                config_result = Database.execute_query(config_query, (subject['subject_config_id'],))

                if config_result and len(config_result) > 0:
                    subject_name = config_result[0]['name']

            # Only add if subject_name is not None and not already in result
            if subject_name and subject_name not in seen_subjects:
                seen_subjects.add(subject_name)
                subject['subject_name'] = subject_name
                result.append(subject)

        print(f"Found {len(result)} unique subjects")
        return jsonify({"Message": "Successfully got subject account", "Data": result}), 200

    except Exception as e:
        print(f"Error in get_subject_account: {str(e)}")
        return jsonify({"Message": f"Error: {e} in getting subject_account"}), 500  # ← Added status code



# =======================================
# ENDPOINT 10: Get Calendar per Room
#========================================
def check_room_id(room_id):
    try:
        query = """
            SELECT COUNT(*) AS nbr FROM room WHERE id = %s
        """
        values = (room_id,)
        result = Database.execute_query(query, values)
        if result and len(result) > 0:
            return result[0]['nbr'] > 0
        return False  # Explicit return for empty results
    except Exception as e:
        print(f"Error checking room_id: {e}")  # Log the error
        return False


@calendar_bp.route('/get-calendar-room/<int:room_id>', methods=['GET'])
def get_calendar_room(room_id):
    try:
        # Validate room exists first
        if not check_room_id(room_id):
            return jsonify({"Message": "Room not found"}), 404

        query = """
            SELECT * FROM relation_calander_group_session WHERE room_id = %s
        """
        values = (room_id,)
        result = Database.execute_query(query, values)

        if result and len(result) > 0:
            # Convert datetime objects to ISO format strings
            for item in result:
                if 'start_time' in item and item['start_time']:
                    item['start_time'] = item['start_time'].isoformat()
                if 'end_time' in item and item['end_time']:
                    item['end_time'] = item['end_time'].isoformat()
                if 'created_at' in item and item['created_at']:
                    item['created_at'] = item['created_at'].isoformat()
                if 'updated_at' in item and item['updated_at']:
                    item['updated_at'] = item['updated_at'].isoformat()
                if 'timestamp' in item and item['timestamp']:
                    item['timestamp'] = item['timestamp'].isoformat()

            return jsonify({"Message": "Successfully got calendar room", "Data": result}), 200
        else:
            return jsonify({"Message": "No calendar data found for this room"}), 404

    except Exception as e:
        print(f"Error in get_calendar_room: {e}")
        return jsonify({"Message": f"Error: {e} coming from get calendar room"}), 500



# =======================================
# ENDPOINT 11: Create calander request
#========================================
def check_session(session_id):
    try:
        query = """SELECT COUNT(*) AS nbr FROM session WHERE id = %s"""
        values = (session_id,)
        result = Database.execute_query(query,values)
        if result and len(result) > 0:
            return result[0]['nbr'] > 0
        return False
    except Exception:
        return False

def check_group(group_id):
    try:
        query = """SELECT COUNT(*) AS nbr FROM relation_group_local_session WHERE id = %s"""
        values = (group_id,)
        result = Database.execute_query(query,values)
        if result and len(result)> 0 :
            return result[0]['nbr']>0
        return False

    except Exception as e:
        return False

def check_user(user_id):
    try:
        query = """SELECT COUNT(*) AS nbr FROM user WHERE id = %s """
        values = (user_id,)
        result = Database.execute_query(query,values)
        if result and len(result)> 0:
            return result[0]['nbr']
    except Exception:
        return False

def check_subject(subject_id):
    try:
        query =""" SELECT COUNT(*) AS nbr FROM subject_config where id = %s """
        values = (subject_id,)
        result = Database.execute_query(query,values)
        if result and len(result)>0:
            return result[0]['nbr']

    except Exception :
        return False






# ================================ NOTIFICATION PART ================================

def save_notification(notification_payload, user_id):
    try:
        query = """
            INSERT INTO notification (user_id, title, message, type, notif_data)
            VALUES (%s, %s, %s, %s, %s) 
        """
        values = (
            user_id,
            notification_payload.get('title', 'New Notification'),
            notification_payload.get('message', ''),
            "tablet_notif",
            json.dumps(notification_payload)  # Convert dict to JSON string
        )
        Database.execute_query(query, values)
        return True
    except Exception as e:
        print(f"❌ Failed to save notification: {e}")
        return False


def send_notification(notification_payload):
    # Save notification to database FIRST (so it's always stored)
    user_id = notification_payload.get('account_id')

    if user_id:
        save_notification(notification_payload, user_id)

    # Then send real-time notification to Academie Platform
    try:
        academie_url = "https://172.28.20.178:5015/api/notify-calendar-request"
        response = requests.post(
            academie_url,
            json=notification_payload,
            verify=False,
            timeout=5
        )

        if response.status_code == 200:
            print(f"✅ Notification sent to Academie Platform for account ")
        else:
            print(f"⚠️ Failed to send notification: {response.status_code}")
            print(f"⚠️ Response content: {response.text}")

    except requests.exceptions.Timeout as timeout_error:
        print(f"⏱️ Timeout error: {timeout_error}")
    except requests.exceptions.ConnectionError as conn_error:
        print(f"🔌 Connection error: {conn_error}")
    except requests.exceptions.RequestException as req_error:
        print(f"❌ Request error: {req_error}")
    except Exception as notify_error:
        print(f"⚠️ Unexpected error sending notification: {type(notify_error).__name__}")
        print(f"⚠️ Error details: {notify_error}")
        import traceback
        print(f"⚠️ Traceback:\n{traceback.format_exc()}")



@calendar_bp.route('/create-calander_request/<int:session_id>', methods=['POST'])
def create_calander_request(session_id):
    try:
        if not (check_session(session_id)):
            return jsonify({
                "Message": "There is no session_id"
            }), 404

        calander_data = request.get_json()

        room_id = calander_data.get('room_id')
        group_id = calander_data.get('group_id')
        subject_id = calander_data.get('subject_id')
        user_id = calander_data.get('user_id')
        completion_tag = calander_data.get('tag')
        duplicate = calander_data.get('duplicate')
        start_date = calander_data.get('start_date')
        start_time = calander_data.get('start_time')
        end_time = calander_data.get('end_time')
        end_date = calander_data.get('end_date')
        description = calander_data.get('description')
        account_id = calander_data.get('account_id')
        create_time = datetime.now()
        type_session = calander_data.get('type')

        # Convert list to comma-separated string
        if isinstance(completion_tag, list):
            completion_tag = ','.join(map(str, completion_tag))

        # Convert empty strings to None for date/time fields
        if start_date == '' or start_date is None:
            start_date = None
        if end_date == '' or end_date is None:
            end_date = None
        if start_time == '' or start_time is None:
            start_time = None
        if end_time == '' or end_time is None:
            end_time = None

        if not (check_room_id(room_id) and check_user(user_id) and check_subject(subject_id) and check_group(group_id)):
            return jsonify({"Message": "Invalid params"}), 400

        query = """INSERT INTO calendar_request(
                        session_id, group_id, room_id, subject_id, user_id,
                        completion_tags, duplicate, start_date, start_time, end_time, end_date,
                        description, account_id, type, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );"""

        values = (session_id, group_id, room_id, subject_id, user_id, completion_tag, duplicate,
                  start_date, start_time, end_time, end_date, description, account_id, type_session, create_time)

        result = Database.execute_query(query, values, fetch=False)
        if result:
            notification_payload = {
                    'request_id': result,
                    'account_id': account_id,
                    'session_id': session_id,
                    'room_id': room_id,
                    'group_id': group_id,
                    'subject_id': subject_id,
                    'user_id': user_id,
                    'description': description,
                    'start_date': str(start_date) if start_date else None,
                    'start_time': str(start_time) if start_time else None,
                    'end_time': str(end_time) if end_time else None,
                    'end_date': str(end_date) if end_date else None,
                    'type': type_session,
                    'created_at': create_time.strftime('%Y-%m-%d %H:%M:%S')
                 }
            send_notification(notification_payload)
            return jsonify({
                "success":True,
                "message":"Calendar request created successfully"
            })

        else:
            return jsonify({"bad":""}),404


    except Exception as e:
        print(f"❌ Query error: {e}")
        import traceback
        print(f"❌ Traceback:\n{traceback.format_exc()}")
        return jsonify({
            "Message": "Error in create_calendar_request",
            "error": str(e)
        }), 500


# =======================================
# ENDPOINT 12: get calander request
#========================================
@calendar_bp.route('/get-calander_request/<int:room_id>', methods=['GET'])
def get_calander_request(room_id):
    try:
        if not (check_room_id(room_id)):
            return jsonify({
                "Message": f"Error: this room doesn't exist"
            }), 404

        query = """
            SELECT 
                cr.id,
                cr.session_id,
                cr.group_id,
                cr.type,
                cr.room_id,
                cr.subject_id,
                cr.user_id,
                u.username,
                cr.completion_tags,
                cr.duplicate,
                cr.start_time,
                cr.end_time,
                cr.end_date,
                cr.description,
                cr.account_id,
                cr.accepted,
                cr.created_at,
                cr.updated_at,
                cr.enabled,
                cr.start_date,
                grp.name AS group_name,
                s.name AS session_name,
                CASE 
                    WHEN sc.name = 'other' THEN acs.other_subject
                    ELSE sc.name
                END AS subject_name
            FROM calendar_request cr
            INNER JOIN relation_group_local_session grp ON cr.group_id = grp.id
            INNER JOIN session s ON cr.session_id = s.id
            INNER JOIN subject_config sc ON cr.subject_id = sc.id
            INNER JOIN user u ON cr.user_id = u.id
            LEFT JOIN account_subject acs ON cr.subject_id = acs.id AND sc.name = 'other'
            WHERE cr.room_id = %s 
                AND cr.accepted = 0 
                AND cr.enabled = 1
        """
        values = (room_id,)
        result = Database.execute_query(query, values)

        if result:
            # Convert the result to JSON-serializable format
            serialized_result = []
            for row in result:
                serialized_row = {
                    'start_date': row['start_date'],
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'group_id': row['group_id'],
                    'type': row['type'],
                    'room_id': row['room_id'],
                    'subject_id': row['subject_id'],
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'completion_tags': row['completion_tags'],
                    'duplicate': row['duplicate'],
                    # Convert timedelta to string (HH:MM:SS format)
                    'start_time': str(row['start_time']) if row['start_time'] else None,
                    'end_time': str(row['end_time']) if row['end_time'] else None,
                    # Convert date to string (YYYY-MM-DD format)
                    'end_date': row['end_date'].strftime('%Y-%m-%d') if row['end_date'] else None,
                    'description': row['description'],
                    'account_id': row['account_id'],
                    'accepted': row['accepted'],
                    # Convert datetime to string (YYYY-MM-DD HH:MM:SS format)
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None,
                    'updated_at': row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else None,
                    'enabled': row['enabled'],
                    # Additional joined fields
                    'group_name': row['group_name'],
                    'session_name': row['session_name'],
                    'subject_name': row['subject_name']
                }
                serialized_result.append(serialized_row)

            return jsonify({
                "Message": "Success",
                "data": serialized_result
            }), 200
        else:
            return jsonify({
                "Message": "No calendar requests found"
            }), 404

    except Exception as e:
        print(f"Error in get_calander_request: {str(e)}")
        return jsonify({
            "Message": f"Error: {str(e)} from get_calander_request"
        }), 500



# =======================================
# ENDPOINT 13: GET NOTIFICATION
# =======================================
@calendar_bp.route('/get-notification/<account_id>', methods=['GET'])
def get_notification(account_id):
    try:
        query = """
            SELECT 
                n.id,
                n.user_id,
                n.title,
                n.message,
                n.type,
                n.is_read,
                n.created_at,
                n.notif_data
            FROM notification n 
            WHERE user_id = %s
            ORDER BY is_read ASC, created_at DESC
        """
        values = (account_id,)
        result = Database.execute_query(query, values)

        if result:
            notifications = []
            unread_count = 0

            for row in result:
                # Parse JSON data if it exists
                notif_data = None
                if row['notif_data']:
                    try:
                        notif_data = json.loads(row['notif_data'])
                    except:
                        notif_data = row['notif_data']

                notification = {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'title': row['title'],
                    'message': row['message'],
                    'type': row['type'],
                    'is_read': bool(row['is_read']),
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'data': notif_data
                }

                notifications.append(notification)

                if not row['is_read']:
                    unread_count += 1

            return jsonify({
                'success': True,
                'notifications': notifications,
                'total': len(notifications),
                'unread_count': unread_count
            }), 200
        else:
            return jsonify({
                'success': True,
                'notifications': [],
                'total': 0,
                'unread_count': 0
            }), 200

    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'notifications': [],
            'total': 0,
            'unread_count': 0
        }), 500




    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from get_notification ",

        }),500


# =======================================
# ENDPOINT 14: GET CALANDER_REQUQST
# =======================================
@calendar_bp.route('/get-calander_request/<int:account_id>', methods=['GET'])
def get_calander_req(account_id):
    try:
        print("\n \n \n \n \n \n \n hiii")
        query = """
            SELECT 
                cr.id,
                cr.session_id,
                cr.group_id,
                cr.type,
                cr.room_id,
                cr.subject_id,
                cr.user_id,
                u.username,
                cr.completion_tags,
                cr.duplicate,
                cr.start_time,
                cr.end_time,
                cr.end_date,
                cr.description,
                cr.account_id,
                cr.accepted,
                cr.created_at,
                cr.updated_at,
                cr.enabled,
                cr.start_date,
                grp.name AS group_name,
                s.name AS session_name,
                CASE 
                    WHEN sc.name = 'other' THEN acs.other_subject
                    ELSE sc.name
                END AS subject_name
            FROM calendar_request cr
            INNER JOIN relation_group_local_session grp ON cr.group_id = grp.id
            INNER JOIN session s ON cr.session_id = s.id
            INNER JOIN subject_config sc ON cr.subject_id = sc.id
            INNER JOIN user u ON cr.user_id = u.id
            LEFT JOIN account_subject acs ON cr.subject_id = acs.id AND sc.name = 'other'
            WHERE
                cr.account_id = %s
                cr.accepted = 0 
                AND cr.enabled = 1
        """
        values=(account_id,)
        result = Database.execute_query(query,values)
        if result:
            # Convert the result to JSON-serializable format
            serialized_result = []
            for row in result:
                serialized_row = {
                    'start_date': row['start_date'],
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'group_id': row['group_id'],
                    'type': row['type'],
                    'room_id': row['room_id'],
                    'subject_id': row['subject_id'],
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'completion_tags': row['completion_tags'],
                    'duplicate': row['duplicate'],
                    # Convert timedelta to string (HH:MM:SS format)
                    'start_time': str(row['start_time']) if row['start_time'] else None,
                    'end_time': str(row['end_time']) if row['end_time'] else None,
                    # Convert date to string (YYYY-MM-DD format)
                    'end_date': row['end_date'].strftime('%Y-%m-%d') if row['end_date'] else None,
                    'description': row['description'],
                    'account_id': row['account_id'],
                    'accepted': row['accepted'],
                    # Convert datetime to string (YYYY-MM-DD HH:MM:SS format)
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None,
                    'updated_at': row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else None,
                    'enabled': row['enabled'],
                    # Additional joined fields
                    'group_name': row['group_name'],
                    'session_name': row['session_name'],
                    'subject_name': row['subject_name']
                }
                serialized_result.append(serialized_row)

            return jsonify({
                "Message": "Success",
                "data": serialized_result
            }), 200
        else:
            return jsonify({
                "Message": "No calendar requests found"
            }), 404




    except Exception as e:
        print(f"Error {e} coming from calander_req")
        return jsonify({
            "Message":"Error"
        }),500

