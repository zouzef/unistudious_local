"""Attendance-related business logic."""
import requests
import time
from datetime import datetime, timedelta
from auth.token_manager import token_manager
from utils.config import config

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = config["url"]["API_BASE_URL"]


def fetch_attendance():
    """Fetch all attendance/calendar data with retry logic."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
            end_point = config["url"]["get_all_calendar"]
            url = f"{base_url}{end_point}"
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 and attempt < max_retries - 1:
                print(f"⚠️ Got 403, refreshing token and retrying...")
                token_manager.refresh_token()
                time.sleep(1)
                continue
            raise
        except requests.RequestException as e:
            print(f"Error fetching attendance: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None


def get_session_for_room(room, attendance):
    """Get active or upcoming session for a room."""
    list_session = [i for i in attendance if i["roomId"] == room]
    if not list_session:
        return None

    now = datetime.now()
    active_or_upcoming_sessions = []

    for session in list_session:
        try:
            session_start = datetime.strptime(session["start"], "%a, %d %b %Y %H:%M:%S %Z")
            session_end = datetime.strptime(session["end"], "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            try:
                session_start = datetime.strptime(session["start"], "%Y-%m-%d %H:%M:%S")
                session_end = datetime.strptime(session["end"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"DEBUG: Could not parse date format for session: {session['start']}")
                continue

        if now <= session_end + timedelta(minutes=5):
            active_or_upcoming_sessions.append(session)

    if not active_or_upcoming_sessions:
        return None

    active_or_upcoming_sessions.sort(key=lambda x: datetime.strptime(x["start"], "%a, %d %b %Y %H:%M:%S %Z")
    if 'GMT' in x["start"]
    else datetime.strptime(x["start"], "%Y-%m-%d %H:%M:%S"))

    return active_or_upcoming_sessions[0]


def get_calendar_details(session_id):
    """Get detailed calendar/attendance info for a session."""
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    end_point = config["url"]["get_attendance"]
    url = f"{base_url}{end_point}/{session_id}"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching attendance: {e}")
        return None


def get_attendance_by_id(session_id, attendance_list):
    """Find attendance record by session ID."""
    for item in attendance_list:
        if item["id"] == session_id:
            return item
    return None


def update_attendance_status(attendance_id, status):
    """Update attendance status for a student."""
    try:
        headers = {
            "Authorization": f"Bearer {token_manager.get_token()}",
            "Content-Type": "application/json"
        }

        payload = {"status": bool(status)}
        endpoint = config["url"]["update_attendance_student"]
        url = f"{base_url}{endpoint}/{attendance_id}"

        print(f"DEBUG: Updating attendance {attendance_id} with payload: {payload}")

        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        result = response.json()
        print(f"DEBUG: Server response: {result}")

        return {"status": "success", "message": "Status updated successfully"}

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request exception in update_attendance_status: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"DEBUG: Server error response: {e.response.text}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"DEBUG: Exception in update_attendance_status: {e}")
        return {"status": "error", "message": str(e)}


def add_attendance_note(attendance_id, note):
    """Add a note to attendance record."""
    try:
        headers = {
            "Authorization": f"Bearer {token_manager.get_token()}",
            "Content-Type": "application/json"
        }
        endpoint = config["url"]["update-attendance-note"]
        url = f"{base_url}{endpoint}/{attendance_id}"

        payload = {"note": note}
        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        return {"status": "success", "message": "Note added successfully"}
    except Exception as e:
        print(f"DEBUG: Exception in add_attendance_note: {e}")
        return {"status": "error", "message": str(e)}


def get_attendance_statistics(calendar_id):
    """Get statistics for a calendar/session."""
    try:
        url = f"{base_url}{config['url']['get_statics_attendance']}/{calendar_id}"
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"DEBUG: Error {e} coming from get_attendance_statistics")
        return {"status": "error", "message": str(e)}


def reset_attendance(calendar_id):
    """Reset all attendance for a calendar/session."""
    try:
        url = f"{base_url}{config['url']['reset_attendance_api']}/{calendar_id}"
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            return {"status": "success", "message": "Attendance reset successfully"}
    except Exception as e:
        print(f"DEBUG: Error {e} from reset_attendance")
        return {"status": "error", "message": str(e)}


def delete_attendance(calendar_id, user_id):
    """Delete attendance for a specific user."""
    try:
        url = f"{base_url}{config['url']['delete_attendance_api']}/{calendar_id}/{user_id}"
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            return {"status": "success", "message": "Attendance deleted successfully"}
    except Exception as e:
        print(f"DEBUG: Error {e} from delete_attendance")
        return {"status": "error", "message": str(e)}


def get_account_data(calendar_id):
    """Get account data for a calendar."""
    try:
        url = f"{base_url}{config['url']['get_data_account']}/{calendar_id}"
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error"}
    except Exception as e:
        print(f"DEBUG: Error {e} from get_account_data")
        return {"status": "error", "message": str(e)}