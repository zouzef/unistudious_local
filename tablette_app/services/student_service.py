"""Student-related business logic."""
import requests
from auth.token_manager import token_manager
from utils.config import config

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = config["url"]["API_BASE_URL"]


def get_unknown_students(calendar_id):
    """Get list of unknown students detected in a session."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        endpoint = config["url"]["show-attendance-unknown"]
        url = f"{base_url}{endpoint}/{calendar_id}"

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print(f"DEBUG: Exception in get_unknown_students: {e}")
        return {'status': 'error', 'message': str(e)}


def get_unknown_student_attendance(calendar_id):
    """Get attendance records for unknown students."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        url = f"{base_url}{config['url']['get_unknown_student_attendance']}/{calendar_id}"

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print(f"DEBUG: Exception in get_unknown_student_attendance: {e}")
        return {'status': 'error', 'message': str(e)}


def associate_folder_to_user(user_id, folder, calendar_id, attendance_id):
    """Associate an unknown student folder to a known user."""
    try:
        url = f"{base_url}{config['url']['associate_folder_user']}/{calendar_id}"
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        payload = {
            "userId": user_id,
            "folder": folder,
            "calanderId": calendar_id,
            "attendanceId": attendance_id
        }

        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        return {'success': True}
    except Exception as e:
        print(f"DEBUG: Exception in associate_folder_to_user: {e}")
        return {'status': 'error', 'message': str(e)}


def get_new_group(calendar_id):
    """Get new group information for a calendar."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        url = f"{base_url}{config['url']['get-group']}/{calendar_id}"

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        return response.json()
    except requests.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
        return {"error": str(http_err)}
    except Exception as err:
        print(f"Exception in get_new_group: {err}")
        return {"error": str(err)}


def get_students_list(calendar_id):
    """Get list of all students that can be added to attendance."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        url = f"{base_url}{config['url']['get_list_add_student_attendance']}/{calendar_id}"

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        data = response.json()

        if 'users' not in data:
            print("No 'users' key in response, returning empty array")
            return {"users": []}

        return data
    except Exception as e:
        print(f"Error: {e}")
        return {"users": []}


def add_student_to_attendance(user_id, calendar_id, group_id, relation_id=None,
                              checkbox1_checked=False, checkbox2_checked=False,
                              selected_group_id=None):
    """Add a student to attendance with group options."""
    try:
        if not user_id or not calendar_id:
            return {"success": False, "error": "userId and calendarId are required"}

        # Initialize variables based on checkbox states
        add_to_group = False
        join_to_group = False
        final_selected_group_id = None
        final_relation_id = None

        # Case 1: Only checkbox2 is checked
        if checkbox2_checked and not checkbox1_checked:
            add_to_group = False
            join_to_group = True
            final_selected_group_id = None
            final_relation_id = relation_id
        # Case 2: Neither checkbox is checked
        elif not checkbox1_checked and not checkbox2_checked:
            add_to_group = False
            join_to_group = False
            final_selected_group_id = None
            final_relation_id = None
        # Case 3: checkbox1 is checked (with or without checkbox2)
        elif checkbox1_checked:
            add_to_group = True
            join_to_group = False
            final_selected_group_id = selected_group_id
            final_relation_id = relation_id

        headers = {
            "Authorization": f"Bearer {token_manager.get_token()}",
        }
        payload = {
            "userId": user_id,
            "calendarId": calendar_id,
            "groupId": group_id,
            "relationId": final_relation_id,
            "addToGroup": add_to_group,
            "selectedGroupId": final_selected_group_id,
            "joinToGroup": join_to_group
        }

        url = f"{base_url}{config['url']['save_user']}"
        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        if response.json().get('success') == False:
            return {
                "success": False,
                "message": "There is no Place for this student"
            }

        return {
            "success": True,
            "message": "Student attendance added successfully",
            "data": response.json()
        }

    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        return {
            "success": False,
            "error": str(e),
            "response": e.response.text if hasattr(e, 'response') else None,
            "status_code": status_code
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": 500
        }


def delete_unknown_student(calendar_id, folder):
    """Delete an unknown student folder."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        payload = {
            "calendarId": calendar_id,
            "folderName": folder,
        }
        url = f"{base_url}{config['url']['delete_unknown_student_attendance']}/{calendar_id}"

        response = requests.delete(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print("DEBUG: Exception in delete_unknown_student:", e)
        return {"error": str(e)}


def delete_image_from_folder(calendar_id, filename, folder):
    """Delete a specific image from an unknown student folder."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        payload = {
            "file_name": filename,
            "folder": folder
        }
        url = f"{base_url}{config['url']['delete_image_from_folder']}/{calendar_id}"

        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            return {"status": "success"}
        else:
            return {"status": "error"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_student_current_group(calendar_id, user_id):
    """Get current group for a student."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        url = f"{base_url}{config['url']['attendance_get_group_student_select']}/{calendar_id}/{user_id}"

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print("DEBUG: Exception in get_student_current_group:", e)
        return None