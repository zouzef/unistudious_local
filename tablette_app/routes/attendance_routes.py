"""Attendance-related API endpoints."""
from flask import Blueprint, jsonify, request
from datetime import datetime
from services.attendance_service import (
    fetch_attendance,
    get_attendance_by_id,
    get_calendar_details,
    update_attendance_status,
    add_attendance_note,
    get_attendance_statistics,
    reset_attendance,
    delete_attendance,
    get_account_data
)

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance/<int:session_id>')
def api_get_attendance(session_id):
    """Get attendance data for a session."""
    try:
        attendance_calendar = fetch_attendance()
        list_attendance = attendance_calendar["data"]
        data = get_attendance_by_id(session_id, list_attendance)

        if data:
            return jsonify(data)
        return jsonify([])

    except Exception as e:
        print(f"DEBUG: Exception in api_get_attendance: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@attendance_bp.route('/calender/<int:session_id>')
def api_get_calendar(session_id):
    """Get calendar/attendance details for a session."""
    try:
        data = get_calendar_details(session_id)
        if data and "attendance" in data:
            return jsonify(data["attendance"])
        return jsonify([])
    except Exception as e:
        print(f"DEBUG: Exception in api_get_calendar: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@attendance_bp.route('/add-note/<int:attendance_id>', methods=['POST'])
def add_note(attendance_id):
    """Add a note to an attendance record."""
    try:
        from tablette_app import socketio  # Import here to avoid circular import

        data = request.get_json()
        note = data.get('note', '')
        session_id = data.get('session_id')

        result = add_attendance_note(attendance_id, note)

        if session_id:
            socketio.emit('note_update', {
                'attendance_id': attendance_id,
                'note': note,
                'timestamp': datetime.now().isoformat()
            }, room=f'session_{session_id}')

        return jsonify(result)
    except Exception as e:
        print(f"DEBUG: Exception in add_note: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@attendance_bp.route('/change-stutatus/<int:id_attendance>', methods=['POST'])
def change_status_student(id_attendance):
    """Change attendance status for a student."""
    try:
        from app import socketio  # Import here to avoid circular import

        data = request.get_json() or {}
        session_id = data.get('session_id')
        is_present = data.get('is_present')

        response = update_attendance_status(id_attendance, is_present)

        if session_id:
            socketio.emit('status_update', {
                'attendance_id': id_attendance,
                'new_status': is_present,
                'timestamp': datetime.now().isoformat()
            }, room=f'session_{session_id}')

        return jsonify(response)
    except Exception as e:
        print(f"DEBUG: Exception in change_status_student: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@attendance_bp.route('/get-statics-attendance/<int:calendar_id>')
def get_statics_attendance(calendar_id):
    """Get attendance statistics for a calendar."""
    try:
        result = get_attendance_statistics(calendar_id)
        return jsonify(result)
    except Exception as e:
        print(f"DEBUG: Error {e} coming from get_statics_attendance")
        return jsonify({"status": "error", "message": str(e)}), 500


@attendance_bp.route('/reset_attendance_api/<int:calendar_id>')
def reset_attendance_api(calendar_id):
    """Reset all attendance for a calendar."""
    try:
        from tablette_app import socketio  # Import here to avoid circular import

        result = reset_attendance(calendar_id)

        if result.get("status") == "success":
            socketio.emit('reset_attendance', {'message': 'Reset attendance triggered'})
            return jsonify({"status": "success", "message": "success from reset_attendance_api"}), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        print(f"DEBUG: Error {e} come from reset_attendance_api")
        return jsonify({"status": "error", "message": "error from reset_attendance_api"}), 500


@attendance_bp.route('/delete_attendance_api/<int:calendar_id>/<int:user_id>')
def delete_attendance_api(calendar_id, user_id):
    """Delete attendance for a specific user."""
    try:
        from tablette_app import socketio  # Import here to avoid circular import

        result = delete_attendance(calendar_id, user_id)

        if result.get("status") == "success":
            socketio.emit('delete_attendance', {'message': 'Delete attendance triggered'})
            return jsonify({"status": "success", "message": "success from delete_attendance_api"}), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        print(f"DEBUG: Error {e} come from delete_attendance_api")
        return jsonify({"status": "error", "message": "error from delete_attendance_api"}), 500


@attendance_bp.route('/get-data-account/<int:calendar_id>')
def get_data_account_route(calendar_id):
    """Get account data for a calendar."""
    try:
        result = get_account_data(calendar_id)
        return jsonify(result)
    except Exception as e:
        print(f"DEBUG: Error {e} come from get_data_account")
        return jsonify({"status": "error", "message": "error from get_data_account"}), 500


@attendance_bp.route('/trigger-update/<int:session_id>')
def trigger_update(session_id):
    """Manually trigger an update (for testing/debugging)."""
    from tablette_app import socketio  # Import here to avoid circular import

    socketio.emit('test_update', {
        'message': 'Manual update triggered',
        'session_id': session_id,
        'timestamp': datetime.now().isoformat()
    }, room=f'session_{session_id}')

    return jsonify({"status": "success", "message": "Update triggered"})