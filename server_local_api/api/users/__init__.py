from flask import Blueprint, jsonify, request
from datetime import datetime
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# Create blueprint
students_bp = Blueprint('students', __name__, url_prefix='/scl')


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


@students_bp.route('/attendance-save-user', methods=['POST'])
@token_required
def add_student_api():
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

        # CASE 1: Move user to a new group
        if addToGroup and selectedGroupId is not None and not joinToGroup:
            query = """
                SELECT id FROM relation_user_session
                WHERE user_id = %s AND session_id = %s
                  AND relation_group_local_session_id IS NOT NULL
                  AND enabled = 1
                ORDER BY id ASC LIMIT 1
            """
            relation = Database.execute_query(query, (userId, session_id))

            if not relation:
                return jsonify({"success": False, "error": "User not assigned to any group yet"}), 400

            rel_id = relation[0]['id']

            query = """
                UPDATE relation_user_session
                SET relation_group_local_session_id = %s
                WHERE id = %s
            """
            Database.execute_query(query, (current_group_id, rel_id), fetch=False)

            final_group_id = selectedGroupId

        # CASE 2: Join user to current calendar's group
        elif joinToGroup and not addToGroup:
            query = """
                SELECT id FROM relation_user_session
                WHERE user_id = %s AND session_id = %s
                  AND relation_group_local_session_id IS NULL
                  AND enabled = 1
                LIMIT 1
            """
            relation = Database.execute_query(query, (userId, session_id))

            if not relation:
                return jsonify({"success": False, "error": "User already in a group or no relation"}), 400

            rel_id = relation[0]['id']

            query = """
                UPDATE relation_user_session
                SET relation_group_local_session_id = %s
                WHERE id = %s
            """
            Database.execute_query(query, (current_group_id, rel_id), fetch=False)

        # CASE 3: Normal attendance
        elif not addToGroup and not joinToGroup and selectedGroupId is None and relationId is None:
            pass  # Just insert attendance below

        else:
            return jsonify({"success": False, "error": "Invalid parameters"}), 400

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

        # Insert audit trail
        insert_attendance_audit(attendance_id, userId, calendarId, final_group_id,
                                relationId, addToGroup, selectedGroupId, joinToGroup)

        return jsonify({
            "success": True,
            "message": "Student attendance added successfully",
            "attendance_id": attendance_id
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500