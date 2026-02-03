from flask import Blueprint, jsonify, request
from datetime import datetime
import sys
import os
import json

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# Create ONE blueprint for all attendance endpoints
attendance_bp = Blueprint('attendance', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Get attendance by calendar
# ========================================
@attendance_bp.route('/get-attendance/<int:calendar_id>', methods=['GET'])
@token_required
def get_todays_attendance(calendar_id):
    try:
        query = """
            SELECT 
                a.id,
                u.full_name as full_name,
                a.user_id as userId,
                u.ref_slc as userRefRlc,
                a.session_id as session,
                a.account_id as account,
                MAX(rus.relation_group_local_session_id) as `group`,
                a.is_present as isPresent,
                a.day as day,
                a.calander_id as calander,
                a.note as note,
                a.updated_at as updatedAt
            FROM attendance a
            LEFT JOIN user u ON a.user_id = u.id
            LEFT JOIN relation_user_session rus ON a.user_id = rus.user_id 
                AND a.session_id = rus.session_id
            WHERE a.calander_id = %s
                AND (rus.enabled = 1 OR rus.enabled IS NULL) AND a.enabled=1
            GROUP BY a.id, u.full_name, a.user_id, u.ref_slc, a.session_id, 
                     a.account_id, a.is_present, a.day, a.calander_id, 
                     a.note, a.updated_at
        """

        rows = Database.execute_query(query, (calendar_id,))

        formatted_rows = []
        for row in rows:
            formatted_row = {
                "id": row['id'],
                "userName": row['full_name'],
                "userId": row['userId'],
                "userRefRlc": row['userRefRlc'],
                "session": row['session'],
                "account": row['account'],
                "group": row['group'],
                "isPresent": bool(row['isPresent']),
                "day": str(row['day']) if row['day'] else None,
                "calander": row['calander'],
                "note": row['note'],
                "updatedAt": str(row['updatedAt']) if row['updatedAt'] else None
            }
            formatted_rows.append(formatted_row)

        return jsonify({"attendance": formatted_rows}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 2: Get student's groups for attendance
# ========================================
@attendance_bp.route('/attendance-get-group-student-select/<int:calendarId>/<int:userId>', methods=["GET"])
@token_required
def get_attendance_group_student(calendarId, userId):
    try:
        account_id = userId

        # Get session_id from calendar
        query = "SELECT session_id FROM relation_calander_group_session WHERE id = %s"
        calendar_result = Database.execute_query(query, (calendarId,))

        if not calendar_result:
            return jsonify({'error': 'Calendar not found'}), 404

        session_id = calendar_result[0]['session_id']

        # Get user's group assignments
        query = """
            SELECT id, relation_group_local_session_id 
            FROM relation_user_session 
            WHERE session_id = %s AND user_id = %s AND relation_group_local_session_id IS NOT NULL
        """
        student_group = Database.execute_query(query, (session_id, account_id))

        if not student_group:
            return jsonify({'groups': []}), 200

        # Extract unique group IDs
        group_ids = list(set(group['relation_group_local_session_id'] for group in student_group))

        # Get group details
        placeholders = ', '.join(['%s'] * len(group_ids))
        query = f"SELECT id, name FROM relation_group_local_session WHERE session_id = %s AND id IN ({placeholders})"
        groups = Database.execute_query(query, (session_id, *group_ids))

        # Build result
        result_groups = []
        for student_rec in student_group:
            group_id = student_rec['relation_group_local_session_id']
            matching_group = next((g for g in groups if g['id'] == group_id), None)
            if matching_group:
                result_groups.append({
                    "relationId": student_rec['id'],
                    "id": matching_group['id'],
                    "name": matching_group['name']
                })

        return jsonify({"groups": result_groups}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 3: Add user attendance
# ========================================
def insert_attendance_audit(attendance_id, userId, calendarId, groupId,
                            relationId, addToGroup, selectedGroupId, joinToGroup,
                            action_type="ADD_STUDENT"):
    """Insert audit trail for attendance actions"""
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    audit_data = {
        "userId": userId,
        "calendarId": calendarId,
        "groupId": groupId,
        "relationId": relationId,
        "addToGroup": addToGroup,
        "selectedGroupId": selectedGroupId,
        "joinToGroup": joinToGroup
    }
    new_data_json = json.dumps(audit_data)

    query = """
        INSERT INTO attendance_audit 
        (action_type, new_data, changed_at, is_synced, id_attendance)
        VALUES (%s, %s, %s, %s, %s)
    """
    Database.execute_query(query, (action_type, new_data_json, formatted_time, 0, attendance_id), fetch=False)


@attendance_bp.route('/attendance-save-user', methods=['POST'])
@token_required
def add_student_attendance():
    try:
        data = request.get_json()
        print("Incoming request:", data)

        # Extract and validate required fields
        userId = data.get('userId')
        calendarId = data.get('calendarId')
        addToGroup = data.get('addToGroup') == True
        joinToGroup = data.get('joinToGroup') == True
        selectedGroupId = data.get('selectedGroupId')
        relationId = data.get('relationId')

        if not userId or not calendarId:
            return jsonify({"success": False, "error": "Missing userId or calendarId"}), 400

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get calendar/session info
        query = """
            SELECT session_id, account_id, group_session_id
            FROM relation_calander_group_session
            WHERE id = %s AND enabled = 1
        """
        calendar_info = Database.execute_query(query, (calendarId,))

        if not calendar_info:
            return jsonify({"success": False, "error": "Calendar not found or disabled"}), 404

        session_id = calendar_info[0]['session_id']
        account_id = calendar_info[0]['account_id']
        current_group_id = calendar_info[0]['group_session_id']

        # Prevent duplicate attendance
        query = """
            SELECT id FROM attendance
            WHERE user_id = %s AND session_id = %s AND calander_id = %s AND enabled = 1
        """
        if Database.execute_query(query, (userId, session_id, calendarId)):
            return jsonify({"success": False, "error": "User already marked present"}), 400

        # Generate next attendance ID
        query = "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM attendance"
        new_attendance_id = Database.execute_query(query)[0]['next_id']

        final_group_id = current_group_id

        # CASE 1: Move user to a new group (addToGroup = true)
        if addToGroup and selectedGroupId is not None and not joinToGroup:
            query = """
                SELECT id FROM relation_user_session
                WHERE user_id = %s AND session_id = %s
                  AND relation_group_local_session_id IS NOT NULL
                  AND enabled = 1
                ORDER BY id ASC LIMIT 1
            """
            relation = Database.execute_query(query, (userId, session_id))
            print(relation)

            if not relation:
                return jsonify({"success": False, "error": "User not assigned to any group yet"}), 400

            rel_id = relation[0]['id']
            print(rel_id)
            print(selectedGroupId)

            # Update group
            query = """
                UPDATE relation_user_session
                SET relation_group_local_session_id = %s
                WHERE id = %s
            """
            Database.execute_query(query, (current_group_id, rel_id), fetch=False)

            final_group_id = selectedGroupId

            # Insert attendance record
            query = """
                INSERT INTO attendance
                (id, user_id, session_id, account_id, group_session_id, calander_id,
                 is_present, day, enabled, created_at, slc_edit)
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s, 1, %s, 1)
            """
            attendance_id = Database.execute_query(
                query,
                (new_attendance_id, userId, session_id, account_id, final_group_id, calendarId, now, now),
                fetch=False
            ) or new_attendance_id

            # Final audit
            insert_attendance_audit(attendance_id, userId, calendarId, final_group_id,
                                    relationId, addToGroup, selectedGroupId, joinToGroup)

        # CASE 2: Join user to current calendar's group (joinToGroup = true)
        elif joinToGroup and not addToGroup:
            print("hii")
            query = """
                SELECT id FROM relation_user_session
                WHERE user_id = %s AND session_id = %s
                  AND relation_group_local_session_id IS NULL
                  AND enabled = 1
                LIMIT 1
            """
            relation = Database.execute_query(query, (userId, session_id))
            print("Relation", relation)

            if not relation:
                return jsonify({"success": False, "error": "User already in a group or no relation"}), 400

            rel_id = relation[0]['id']

            query = """
                UPDATE relation_user_session
                SET relation_group_local_session_id = %s
                WHERE id = %s
            """
            Database.execute_query(query, (current_group_id, rel_id), fetch=False)

            # Insert attendance record
            query = """
                INSERT INTO attendance
                (id, user_id, session_id, account_id, group_session_id, calander_id,
                 is_present, day, enabled, created_at, slc_edit)
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s, 1, %s, 1)
            """
            attendance_id = Database.execute_query(
                query,
                (new_attendance_id, userId, session_id, account_id, final_group_id, calendarId, now, now),
                fetch=False
            ) or new_attendance_id

            # Final audit
            insert_attendance_audit(attendance_id, userId, calendarId, final_group_id,
                                    relationId, addToGroup, selectedGroupId, joinToGroup)

        # CASE 3: Normal attendance — no group change
        elif (not addToGroup) and (not joinToGroup) and (selectedGroupId == None) and (relationId == None):
            # Insert attendance record
            query = """
                INSERT INTO attendance
                (id, user_id, session_id, account_id, group_session_id, calander_id,
                 is_present, day, enabled, created_at, slc_edit)
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s, 1, %s, 1)
            """
            attendance_id = Database.execute_query(
                query,
                (new_attendance_id, userId, session_id, account_id, final_group_id, calendarId, now, now),
                fetch=False
            ) or new_attendance_id

            # Final audit
            insert_attendance_audit(attendance_id, userId, calendarId, final_group_id,
                                    relationId, addToGroup, selectedGroupId, joinToGroup)

        else:
            return jsonify({"success": False, "error": "Invalid parameters"}), 400

        return jsonify({
            "success": True,
            "message": "Student attendance added successfully",
            "attendance_id": attendance_id
        }), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


# ========================================
# ENDPOINT 4: Get attendance statistics
# ========================================
@attendance_bp.route('/attendance-statistics/<int:id_calender>', methods=['GET'])
@token_required
def statistics_attendance(id_calender):
    try:
        print(id_calender)

        # Count present students
        query = """
            SELECT COUNT(*) as present_count 
            FROM attendance 
            WHERE is_present = 1 AND calander_id = %s
        """
        present_result = Database.execute_query(query, (id_calender,))
        present_count = present_result[0]['present_count'] if present_result else 0

        # Count absent students
        query = """
            SELECT COUNT(*) as absent_count 
            FROM attendance 
            WHERE is_present = 0 AND calander_id = %s
        """
        absent_result = Database.execute_query(query, (id_calender,))
        absent_count = absent_result[0]['absent_count'] if absent_result else 0

        # Count total students
        query = """
            SELECT COUNT(*) as total_count 
            FROM attendance 
            WHERE calander_id = %s
        """
        total_result = Database.execute_query(query, (id_calender,))
        total_count = total_result[0]['total_count'] if total_result else 0

        return jsonify({
            "present_count": present_count,
            "absent_count": absent_count,
            "total_count": total_count
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 5: Delete attendance
# ========================================
@attendance_bp.route('/delete_attendance_api/<int:calender_id>/<int:user_id>', methods=['DELETE'])
@token_required
def delete_attendance_api(calender_id, user_id):
    try:
        # Check if attendance exists
        query = """
            SELECT * FROM attendance 
            WHERE calander_id = %s AND enabled = 1 AND user_id = %s
        """
        attendance_data = Database.execute_query(query, (calender_id, user_id))

        print(attendance_data)

        if attendance_data:
            # Soft delete: set enabled = 0
            query = """
                UPDATE attendance 
                SET enabled = 0, slc_edit = 1 
                WHERE calander_id = %s AND user_id = %s
            """
            Database.execute_query(query, (calender_id, user_id), fetch=False)

            return jsonify({
                "status": "ok",
                "message": "Attendance deleted successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "No attendance records found for the given calendar_id and user_id"
            }), 404

    except Exception as e:
        print(f"DEBUG: Error {e} coming from delete_attendance api")
        return jsonify({
            "status": "error",
            "message": "Error occurred"
        }), 500


# ========================================
# ENDPOINT 6: Delete attendance by ID
# ========================================
@attendance_bp.route('/attendance-delete-student/<int:id_attendance>', methods=['DELETE'])
@token_required
def delete_attendance_by_id(id_attendance):
    try:
        print(id_attendance)

        # Fixed: Delete by attendance ID, not calendar_id and user_id
        query = """
            UPDATE attendance 
            SET enabled = 0 
            WHERE id = %s
        """
        Database.execute_query(query, (id_attendance,), fetch=False)

        # Check if any row was updated
        query_check = "SELECT * FROM attendance WHERE id = %s"
        result = Database.execute_query(query_check, (id_attendance,))

        if result:
            return jsonify({
                "message": "Attendance record deleted successfully"
            }), 200
        else:
            return jsonify({
                "message": "No attendance record found with the given ID"
            }), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 7: Get list of students to add to attendance
# ========================================
@attendance_bp.route('/list-add-student-attendance/<int:calender_id>', methods=["GET"])
@token_required
def list_add_student_attendance(calender_id):
    try:
        # Step 1: Get current attendance to exclude existing students
        query = """
            SELECT DISTINCT a.user_id as userId
            FROM attendance a
            WHERE a.calander_id = %s AND a.enabled = 1
        """
        attendance_data = Database.execute_query(query, (calender_id,))

        list_student_in = [student["userId"] for student in attendance_data]
        print("list_student_in:", list_student_in)

        # Step 2: Get the session_id for this calendar
        query = "SELECT session_id FROM relation_calander_group_session WHERE id = %s"
        session_row = Database.execute_query(query, (calender_id,))

        if not session_row:
            return jsonify({"error": "No session found for this calendar"}), 404

        session_id = session_row[0]["session_id"]
        print("session_id:", session_id)

        # Step 3: Build query for users in this session but not in attendance
        if list_student_in:
            placeholders = ', '.join(['%s'] * len(list_student_in))
            query = f"""
                SELECT 
                    u.id,
                    u.full_name AS fullName,
                    MIN(r.id) AS relationId
                FROM user u
                INNER JOIN relation_user_session r ON u.id = r.user_id
                WHERE r.session_id = %s
                  AND u.enabled = 1
                  AND r.enabled = 1
                  AND u.id NOT IN ({placeholders})
                GROUP BY u.id, u.full_name
            """
            params = [session_id] + list_student_in
        else:
            query = """
                SELECT 
                    u.id,
                    u.full_name AS fullName,
                    MIN(r.id) AS relationId
                FROM user u
                INNER JOIN relation_user_session r ON u.id = r.user_id
                WHERE r.session_id = %s
                  AND u.enabled = 1
                  AND r.enabled = 1
                GROUP BY u.id, u.full_name
            """
            params = [session_id]

        # Step 4: Execute query
        users = Database.execute_query(query, params)

        # Step 5: Format output
        formatted_users = [
            {
                "id": user["id"],
                "fullName": user["fullName"],
                "relationId": user["relationId"],
                "calendarId": calender_id,
                "groupId": 1
            }
            for user in users
        ]

        return jsonify({"users": formatted_users}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================================
# ENDPOINT 8: Get next attendance session
# ========================================
@attendance_bp.route('/get-next-attendance/<int:calendarId>', methods=['GET'])
@token_required
def get_next_attendance_scl(calendarId):
    try:
        print(f"Looking for next attendance after calendar ID: {calendarId}")

        # Get only the NEXT calendar that starts after the given calendar's start time
        query = """
            SELECT rcgs.*, 
                   rcgs.id as calendar_id,
                   rcgs.title as calendar_name,
                   rcgs.start_time,
                   rcgs.end_time,
                   rcgs.description
            FROM relation_calander_group_session rcgs
            WHERE rcgs.start_time > (
                SELECT start_time 
                FROM relation_calander_group_session 
                WHERE id = %s
            )
            ORDER BY rcgs.start_time ASC
            LIMIT 1
        """
        next_calendar = Database.execute_query(query, (calendarId,))

        if not next_calendar:
            return jsonify({
                "message": "No next calendar found after the given calendar ID",
                "calendar_id": calendarId
            }), 404

        # Format the result
        calendar_data = {
            'id': next_calendar[0]['calendar_id'],
            'name': next_calendar[0].get('calendar_name', ''),
            'start_time': next_calendar[0]['start_time'].strftime('%Y-%m-%d %H:%M:%S') if next_calendar[0]['start_time'] else 'unknown',
            'end_time': next_calendar[0]['end_time'].strftime('%Y-%m-%d %H:%M:%S') if next_calendar[0]['end_time'] else 'unknown',
            'description': next_calendar[0].get('description', '')
        }

        return jsonify({
            "message": "Success",
            "reference_calendar_id": calendarId,
            "next_calendar": calendar_data
        }), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ========================================
# ENDPOINT 9: Get next single attendance (alternative)
# ========================================
@attendance_bp.route('/get-next-single-attendance/<int:calendarId>', methods=['GET'])
@token_required
def get_next_single_attendance(calendarId):
    try:
        print(f"Looking for next single attendance after calendar ID: {calendarId}")

        # Same as above - get only the NEXT calendar
        query = """
            SELECT rcgs.*, 
                   rcgs.id as calendar_id,
                   rcgs.title as calendar_name,
                   rcgs.start_time,
                   rcgs.end_time,
                   rcgs.description
            FROM relation_calander_group_session rcgs
            WHERE rcgs.start_time > (
                SELECT start_time 
                FROM relation_calander_group_session 
                WHERE id = %s
            )
            ORDER BY rcgs.start_time ASC
            LIMIT 1
        """
        next_calendar = Database.execute_query(query, (calendarId,))

        if not next_calendar:
            return jsonify({
                "message": "No next calendar found after the given calendar ID",
                "calendar_id": calendarId
            }), 404

        calendar_data = {
            'id': next_calendar[0]['calendar_id'],
            'name': next_calendar[0].get('calendar_name', ''),
            'start_time': next_calendar[0]['start_time'].strftime('%Y-%m-%d %H:%M:%S') if next_calendar[0]['start_time'] else 'unknown',
            'end_time': next_calendar[0]['end_time'].strftime('%Y-%m-%d %H:%M:%S') if next_calendar[0]['end_time'] else 'unknown',
            'description': next_calendar[0].get('description', '')
        }

        return jsonify({
            "message": "Success",
            "reference_calendar_id": calendarId,
            "next_calendar": calendar_data
        }), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ========================================
# ENDPOINT 10: Get all future attendances (v2)
# ========================================
@attendance_bp.route('/get-next-attendance-v2/<int:calendarId>', methods=['GET'])
@token_required
def get_next_attendance_v2(calendarId):
    try:
        print(f"Looking for next attendance after calendar ID: {calendarId} (Version 2)")

        # Step 1: Get the start_time of the reference calendar
        query = """
            SELECT start_time 
            FROM relation_calander_group_session 
            WHERE id = %s
        """
        current_calendar = Database.execute_query(query, (calendarId,))

        if not current_calendar:
            return jsonify({
                "error": "No calendar records found for the given calendar ID"
            }), 404

        reference_start_time = current_calendar[0]['start_time']
        print(f"Reference calendar start_time: {reference_start_time}")

        # Step 2: Get all calendars after this start_time
        query = """
            SELECT rcgs.*, 
                   rcgs.id as calendar_id,
                   rcgs.title as calendar_name,
                   rcgs.start_time,
                   rcgs.end_time,
                   rcgs.description
            FROM relation_calander_group_session rcgs
            WHERE rcgs.start_time > %s
            ORDER BY rcgs.start_time ASC
        """
        next_calendars = Database.execute_query(query, (reference_start_time,))

        if not next_calendars:
            return jsonify({
                "message": "No future calendars found after the reference time",
                "reference_calendar_id": calendarId,
                "reference_start_time": reference_start_time.strftime('%Y-%m-%d %H:%M:%S')
            }), 404

        # Format results
        calendars_data = []
        for calendar in next_calendars:
            calendar_data = {
                'id': calendar['calendar_id'],
                'name': calendar.get('calendar_name', ''),
                'start_time': calendar['start_time'].strftime('%Y-%m-%d %H:%M:%S') if calendar['start_time'] else 'unknown',
                'end_time': calendar['end_time'].strftime('%Y-%m-%d %H:%M:%S') if calendar['end_time'] else 'unknown',
                'description': calendar.get('description', '')
            }
            calendars_data.append(calendar_data)

        return jsonify({
            "message": "Success",
            "reference_calendar_id": calendarId,
            "reference_start_time": reference_start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_future_calendars": len(calendars_data),
            "calendars": calendars_data
        }), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ========================================
# ENDPOINT 11: Reset attendance for a calendar
# ========================================
@attendance_bp.route('/reset_attendance/<int:calender_id>', methods=['POST'])
# @token_required
def reset_attendance(calender_id):
    try:
        # Check if there are any records to reset
        query = """
            SELECT COUNT(id) as count
            FROM attendance
            WHERE calander_id = %s AND (is_present != 0 OR note IS NOT NULL)
        """
        result = Database.execute_query(query, (calender_id,))
        present_count = result[0]['count']

        if present_count == 0:
            print("All the attendance records are already reset")
            return jsonify({
                "status": "ok",
                "message": "All the attendance records are already reset"
            }), 200
        else:
            # Reset attendance: set is_present=0 and note=NULL
            query = """
                UPDATE attendance 
                SET is_present = 0, note = NULL 
                WHERE calander_id = %s
            """
            Database.execute_query(query, (calender_id,), fetch=False)

            return jsonify({
                "status": "ok",
                "message": "Reset successfully"
            }), 200

    except Exception as e:
        print(f"DEBUG: Error {e} from reset_attendance")
        return jsonify({
            "message": "Something went wrong."
        }), 500


# ========================================
# ENDPOINT 12: Get static attendance counts
# ========================================
@attendance_bp.route('/static_attendance/<int:calander_id>', methods=['GET'])
# @token_required
def static_attendance(calander_id):
    try:
        query = """
            SELECT
                SUM(CASE WHEN is_present = 1 THEN 1 ELSE 0 END) AS present,
                SUM(CASE WHEN is_present = 0 THEN 1 ELSE 0 END) AS absent
            FROM (
                SELECT DISTINCT user_id, is_present
                FROM attendance
                WHERE calander_id = %s AND enabled = 1
            ) AS distinct_attendance
        """
        result = Database.execute_query(query, (calander_id,))

        present_count = result[0]['present'] if result[0]['present'] is not None else 0
        absent_count = result[0]['absent'] if result[0]['absent'] is not None else 0

        return jsonify({
            "status": "ok",
            "message": "static_attendance",
            "data": {
                "present": present_count,
                "absent": absent_count
            }
        }), 200

    except Exception as e:
        print(f"DEBUG: Error {e} from static_attendance api")
        return jsonify({
            "status": "error",
            "message": "Error occurred"
        }), 500


# ========================================
# ENDPOINT 13: Update attendance student status
# ========================================
def get_slc_mac(attendance_id):
    try:
        # Get account_id from attendance
        query = "SELECT account_id FROM attendance WHERE id = %s"
        row = Database.execute_query(query, (attendance_id,))

        if not row:
            print(f"No attendance found for id {attendance_id}")
            return None

        id_account = int(row[0]['account_id'])

        # Get SLC username (mac address)
        query = "SELECT username FROM slc WHERE account_id = %s"
        row = Database.execute_query(query, (id_account,))

        if not row:
            print(f"No SLC record found for account_id {id_account}")
            return None

        mac_address = row[0]['username']
        return mac_address

    except Exception as err:
        print(f"DEBUG: Error {err}")
        return None

@attendance_bp.route('/update-attendance-student/<int:id_attendance>', methods=['POST'])
@token_required
def update_attendance_status(id_attendance):
    try:
        # Get data from request (supports both JSON and form data)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Validate that the payload contains 'status'
        if not data or 'status' not in data:
            return jsonify({"error": "Missing 'status' in request payload"}), 400

        status = data['status']
        print(status)

        # Convert string to boolean if it's form data
        if isinstance(status, str):
            status = status.lower() in ['true', '1', 'yes', 'on']
        elif not isinstance(status, bool):
            return jsonify({"error": "Status must be a boolean value (true/false)"}), 400

        # Get SLC mac address
        mac_address = get_slc_mac(id_attendance)

        # Update attendance status
        query = """
            UPDATE attendance 
            SET is_present = %s,
                updated_at = NOW(),
                releaseToken = 1,
                useToken = %s,
                slc_edit = 1
            WHERE id = %s
        """
        Database.execute_query(query, (status, mac_address, id_attendance), fetch=False)

        return jsonify({
            "message": "Attendance status updated successfully",
            "attendance_id": id_attendance,
            "status": status
        }), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ========================================
# ENDPOINT 14: Update attendance note
# ========================================
@attendance_bp.route('/update-attendance-note/<int:attendanceId>', methods=['POST'])
@token_required
def update_attendance_note(attendanceId):
    try:
        print(f"Received request for attendance ID: {attendanceId}")

        # Get data from request (supports both JSON and form data)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        print(f"Received Payload Data: {data}")

        # Validate that the payload contains 'note'
        if not data or 'note' not in data:
            return jsonify({"error": "Missing 'note' in request payload"}), 400

        note = data['note']
        print(f"Extracted Note: {note}")

        # Validate that note is a string
        if not isinstance(note, str):
            return jsonify({"error": "Note must be a string value"}), 400

        # Update attendance note
        query = """
            UPDATE attendance 
            SET note = %s,
                updated_at = NOW(),
                slc_edit = 1
            WHERE id = %s
        """
        Database.execute_query(query, (note, attendanceId), fetch=False)

        return jsonify({
            "message": "Attendance note updated successfully",
            "attendance_id": attendanceId,
            "note": note
        }), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500