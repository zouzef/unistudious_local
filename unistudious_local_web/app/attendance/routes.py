# app/attendance/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.attendance.service import (
    get_attendance_by_calendar,
    get_list_student,
    update_attendance_status,
    update_attendance_note,
    reset_attendance,
    get_attendance_statistics,
    get_attendance_page_data
)

attendance_bp = Blueprint('attendance', __name__)


# ==========================================
# API ROUTES
# ==========================================

@attendance_bp.route('/api/change-status/<int:status>/<int:attendance_id>')
def api_update_attendance(status, attendance_id):
    """Change attendance status"""
    success, message = update_attendance_status(attendance_id, status)
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"success": False, "message": message}), 500


@attendance_bp.route('/api/change-note/<int:attendance_id>', methods=['POST'])
def api_update_note(attendance_id):
    """Change attendance note"""
    data = request.get_json()
    note = data.get('note', '') if data else ''

    success, message = update_attendance_note(attendance_id, note)
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"success": False, "message": message}), 500


@attendance_bp.route('/api/reset-attendance/<int:calendar_id>', methods=['POST'])
def api_reset_attendance(calendar_id):
    """Reset attendance"""
    success, message = reset_attendance(calendar_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 500


@attendance_bp.route('/api/get-statistic/<int:calendar_id>', methods=['GET'])
def api_get_statistics(calendar_id):
    """Get attendance statistics"""
    result = get_attendance_statistics(calendar_id)
    return jsonify({"Message": "success", "data": result}), 200