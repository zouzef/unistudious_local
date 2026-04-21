# app/calendar/service.py
import requests
from flask import current_app
from datetime import datetime


def get_calendar_per_session(account_id: int, session_id: int) -> list:
    """Get calendar data for a specific session"""
    url = f"{current_app.config['BASE_URL']}get_calendar_session/{session_id}/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[CALENDAR ERROR] get_calendar_per_session: {e}")
        return []


def get_calendar_by_id(calendar_id: int) -> dict:
    """Get calendar detail by id"""
    url = f"{current_app.config['BASE_URL']}get_calander_id/{calendar_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', {})
    except Exception as e:
        print(f"[CALENDAR ERROR] get_calendar_by_id: {e}")
        return {}


def delete_calendar_interval(session_id: int, start_date: str, end_date: str) -> tuple:
    """Delete calendar interval"""
    url = f"{current_app.config['BASE_URL']}deleting_interval/{session_id}"
    try:
        # Validate dates
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')

        payload = {
            'start_date': f"{start_date} 00:00:00",
            'end_date':   f"{end_date} 23:59:59"
        }

        response = requests.post(url, json=payload, verify=False, timeout=10)

        if response.status_code == 200:
            return True, "Calendar interval deleted successfully"
        else:
            return False, "Failed to delete interval"

    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"
    except Exception as e:
        print(f"[CALENDAR ERROR] delete_calendar_interval: {e}")
        return False, "Connection error"


def create_calendar(data: dict) -> tuple:
    """Create a new calendar"""
    url = f"{current_app.config['BASE_URL']}create_calander"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)

        if response.status_code == 201:
            return True, "Calendar created successfully"
        elif response.status_code == 402:
            return False, response.json()
        else:
            return False, "Failed to create calendar"

    except Exception as e:
        print(f"[CALENDAR ERROR] create_calendar: {e}")
        return False, "Connection error"


def get_calendar_request(account_id: int) -> list:
    """Get calendar requests"""
    url = f"{current_app.config['BASE_URL']}get-calander_requestt/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[CALENDAR ERROR] get_calendar_request: {e}")
        return []


def approve_calendar_request(calendar_request_id: int) -> tuple:
    """Approve calendar request"""
    url = f"{current_app.config['BASE_URL']}approve_calander_request/{calendar_request_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        print(f"[CALENDAR ERROR] approve_calendar_request: {e}")
        return {"Message": str(e)}, 500


def reject_calendar_request(calendar_request_id: int) -> tuple:
    """Reject calendar request"""
    url = f"{current_app.config['BASE_URL']}reject_calander_request/{calendar_request_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        return True, "Request rejected successfully"
    except Exception as e:
        print(f"[CALENDAR ERROR] reject_calendar_request: {e}")
        return False, "Connection error"


def delete_calendar_request(calendar_request_id: int) -> tuple:
    """Delete calendar request"""
    url = f"{current_app.config['BASE_URL']}delete_calander_request/{calendar_request_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        return True, "Request deleted successfully"
    except Exception as e:
        print(f"[CALENDAR ERROR] delete_calendar_request: {e}")
        return False, "Connection error"


def get_notification(account_id: int) -> dict:
    """Get notifications for account"""
    url = f"{current_app.config['BASE_URL']}get-notification/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[CALENDAR ERROR] get_notification: {e}")
        return {}