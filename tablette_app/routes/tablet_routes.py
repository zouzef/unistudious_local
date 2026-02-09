"""Tablet-related API endpoints."""
from flask import Blueprint, render_template, session, jsonify
from datetime import datetime, timedelta
from services.tablet_service import (
    fetch_all_tablets,
    is_tablet_registered,
    get_tablet_room,
    get_room_name,
    fetch_slc_info
)
from services.attendance_service import (
    fetch_attendance,
    get_session_for_room
)

tablet_bp = Blueprint('tablet', __name__)


@tablet_bp.route('/tablet/<tablet_id>')
def tablet_page(tablet_id):
    """Display tablet page with current session info."""
    try:
        print("hii")
        tablette = fetch_all_tablets()
        if not is_tablet_registered(tablet_id, tablette):
            return render_template("not_found.html", message="Tablet not registered")

        session['tablet_id'] = tablet_id

        # Get room from tablet
        room = get_tablet_room(tablet_id, tablette)

        # Get all scheduled sessions
        attendance_calendar = fetch_attendance()


        if not attendance_calendar or "data" not in attendance_calendar:
            return render_template("no_session.html",
                                   message="No sessions found",
                                   room_id=room,
                                   tablet_id=tablet_id)

        # Find the session for this tablet's room
        session_room = get_session_for_room(room, attendance_calendar["data"])

        if not session_room:
            return render_template("no_session.html",
                                   message="No session for this room",
                                   room_id=room,

                                   tablet_id=tablet_id)

        calender_id = session_room.get("id")
        slc_info = fetch_slc_info()
        slc_id = slc_info.get('Data', {}).get('id') if slc_info and isinstance(slc_info.get('Data'), dict) else None

        # Parse session times
        session_start_str = session_room.get("start")
        session_end_str = session_room.get("end")

        if not session_start_str or not session_end_str:
            return render_template("no_session.html",
                                   message="Session time data is missing",
                                   room_id=room,
                                   tablet_id=tablet_id)

        try:
            # Try the new format first
            session_start = datetime.strptime(session_start_str, "%a, %d %b %Y %H:%M:%S %Z")
            session_end = datetime.strptime(session_end_str, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            # Fallback to the original format
            session_start = datetime.strptime(session_start_str, "%Y-%m-%d %H:%M:%S")
            session_end = datetime.strptime(session_end_str, "%Y-%m-%d %H:%M:%S")

        now = datetime.now()

        # Show session only if current time is within the session duration
        if session_start - timedelta(minutes=5) <= now <= session_end:
            # Get room name from tablets data
            room_name = get_room_name(room, tablette)

            return render_template(
                "index.html",
                tablet_id=tablet_id,
                session_info=session_room,
                room_name=room_name,
                calendar_id = calender_id ,
                slc_id = slc_id
            )

        return render_template("no_session.html",
                               message="No ongoing session at the moment",
                               tablet_id=tablet_id)

    except Exception as e:
        print(f"DEBUG: Exception in tablet_page: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@tablet_bp.route('/tablet/<tablet_id>/check_session')
def check_session(tablet_id):
    """Check if there's an active session for this tablet."""
    try:
        tablette = fetch_all_tablets()

        if not is_tablet_registered(tablet_id, tablette):
            return jsonify({'status': 'no_session'})

        room = get_tablet_room(tablet_id, tablette)

        attendance_calendar = fetch_attendance()

        if not attendance_calendar or "data" not in attendance_calendar:
            print("DEBUG: No attendance calendar data")
            return jsonify({'status': 'no_session'})

        session_room = get_session_for_room(room, attendance_calendar["data"])

        if not session_room:
            return jsonify({'status': 'no_session'})

        # Parse the date strings with the correct format
        try:
            session_start = datetime.strptime(session_room.get("start"), "%a, %d %b %Y %H:%M:%S %Z")
            session_end = datetime.strptime(session_room.get("end"), "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            # Fallback to the original format
            session_start = datetime.strptime(session_room.get("start"), "%Y-%m-%d %H:%M:%S")
            session_end = datetime.strptime(session_room.get("end"), "%Y-%m-%d %H:%M:%S")

        now = datetime.now()

        if session_start - timedelta(minutes=5) <= now <= session_end:
            return jsonify({'status': 'active'})

        print("DEBUG: Session is not active")
        return jsonify({'status': 'no_session'})

    except Exception as e:
        print(f"DEBUG: Exception in check_session: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@tablet_bp.route('/test-images')
def test_images():
    """Test route for images."""
    return render_template('test2.html')