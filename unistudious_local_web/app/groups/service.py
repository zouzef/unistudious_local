# app/groups/service.py
import requests
from flask import current_app


def get_groups(account_id: int, session_id: int) -> list:
    """Get groups with students"""
    url = f"{current_app.config['BASE_URL']}get-group/{account_id}/{session_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[GROUP ERROR] get_groups: {e}")
        return []


def delete_group(group_id: int) -> tuple:
    """Delete a group"""
    url = f"{current_app.config['BASE_URL']}delete-group/{group_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "Group deleted successfully"
        return False, "Group not deleted"
    except Exception as e:
        print(f"[GROUP ERROR] delete_group: {e}")
        return False, "Connection error"


def delete_user_from_group(session_id: int, user_id: int) -> tuple:
    """Delete user from group"""
    url = f"{current_app.config['BASE_URL']}delete-user-from-group/{session_id}/{user_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "User deleted from group successfully"
        return False, "Error deleting user from group"
    except Exception as e:
        print(f"[GROUP ERROR] delete_user_from_group: {e}")
        return False, "Connection error"


def get_users_not_affected(session_id: int, account_id: int) -> list:
    """Get users not affected to any group"""
    url = f"{current_app.config['BASE_URL']}user_not_affected/{session_id}/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('students', [])
    except Exception as e:
        print(f"[GROUP ERROR] get_users_not_affected: {e}")
        return []


def affect_user(session_id: int, user_id: int, group_id: int) -> tuple:
    """Affect user to a group"""
    url = f"{current_app.config['BASE_URL']}affect_user_group/{session_id}"
    try:
        payload = {
            "user_id": user_id,
            "group_id": group_id
        }
        response = requests.post(url, json=payload, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, response.json()
        return False, "Failed to affect student"
    except Exception as e:
        print(f"[GROUP ERROR] affect_user: {e}")
        return False, "Connection error"


def get_subject_group(account_id: int) -> dict:
    """Get subjects for account"""
    url = f"{current_app.config['BASE_URL']}get-subject-account/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[GROUP ERROR] get_subject_group: {e}")
        return {}


def create_group(session_id: int, data: dict) -> tuple:
    """Create a new group"""
    url = f"{current_app.config['BASE_URL']}create_group/{session_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        return response.json(), response.status_code
    except Exception as e:
        print(f"[GROUP ERROR] create_group: {e}")
        return {"Message": "Connection error"}, 500


def update_group(group_id, data):
    try:
        response = requests.post(
			f"{current_app.config['BASE_URL']}update_group/{group_id}",
			json=data,verify=False,timeout=10
		)
        try:
            body = response.json()
        except ValueError:
            body = {"Message": "Invalid response from server"}
        return body, response.status_code
    except Exception as e:
        return {"Message": f"Error: {e} coming from update_group service"}, 500

def disaffect_user_session_service(session_id: int, data: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}disaffect_user_group/{session_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        return response.status_code==200 ,response
    except Exception as e:
        return False,None