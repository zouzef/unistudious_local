# app/calendar/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.calendar.service import (
    get_calendar_per_session,
    get_calendar_by_id,
    delete_calendar_interval,
    create_calendar,
    get_calendar_request,
    approve_calendar_request,
    reject_calendar_request,
    delete_calendar_request,
    get_notification
)

calendar_bp = Blueprint('calendar', __name__)




# ==========================================
# API ROUTES
# ==========================================

@calendar_bp.route('/dashboard/get_calander_per_session/<int:account_id>/<int:session_id>', methods=['GET'])
def api_get_calendar_per_session(account_id, session_id):
    """Get calendar data as JSON"""

    result = get_calendar_per_session(account_id, session_id)
    return jsonify({'success': True, 'data': result}), 200


@calendar_bp.route('/api/delete-calander/<int:session_id>', methods=['DELETE', 'POST'])
def api_delete_calendar(session_id):
    """Delete calendar interval"""
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not start_date or not end_date:
        return jsonify({"message": "Missing start_date or end_date"}), 400

    success, message = delete_calendar_interval(session_id, start_date, end_date)

    if success:
        return jsonify({"message": message}), 200
    return jsonify({"message": message}), 400


@calendar_bp.route('/api/create-calander', methods=['POST'])
def api_create_calendar():
    """Create a new calendar"""
    data = request.get_json()
    success, message = create_calendar(data)

    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 400


@calendar_bp.route('/api/get-calendar-request/<int:account_id>', methods=['GET'])
def api_get_calendar_request(account_id):
    """Get calendar requests"""
    result = get_calendar_request(account_id)
    return jsonify(result), 200


@calendar_bp.route('/api/approve-calander-request/<int:calendar_request_id>', methods=['POST'])
def api_approve_calendar_request(calendar_request_id):
    """Approve calendar request"""
    result, status_code = approve_calendar_request(calendar_request_id)
    return jsonify(result), status_code


@calendar_bp.route('/api/reject-calander-request/<int:calendar_request_id>', methods=['POST'])
def api_reject_calendar_request(calendar_request_id):
    """Reject calendar request"""
    success, message = reject_calendar_request(calendar_request_id)
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"Message": message}), 500


@calendar_bp.route('/api/delete-calander-request/<int:calendar_request_id>', methods=['POST'])
def api_delete_calendar_request(calendar_request_id):
    """Delete calendar request"""
    success, message = delete_calendar_request(calendar_request_id)
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"Message": message}), 500


@calendar_bp.route('/api/get-notification/<int:account_id>', methods=['GET'])
def api_get_notification(account_id):
    """Get notifications"""
    result = get_notification(account_id)
    return jsonify(result), 200