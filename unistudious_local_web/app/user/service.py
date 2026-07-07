# app/user/service.py
import requests
from flask import current_app


def get_all_users(account_id: int) -> dict:
    """Get all users"""
    url = f"{current_app.config['BASE_URL']}get-all-users/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[USER ERROR] get_all_users: {e}")
        return {}

def get_profile_image(user_id: int):
    """Get profile image — returns (content, mimetype)"""
    url = f"{current_app.config['BASE_URL']}get-profile-image/{user_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.content, response.headers.get('Content-Type', 'image/png')
    except Exception as e:
        print(f"[USER ERROR] get_profile_image: {e}")
        return None, None

def update_user(user_id: int, data: dict) -> tuple:
    """Update a real user on the remote server"""
    url = f"{current_app.config['BASE_URL']}update-user/{user_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        return True, "User updated successfully"
    except requests.exceptions.HTTPError as e:
        try:
            err_body = response.json()
        except Exception:
            err_body = response.text
        print(f"[USER ERROR] update_user HTTP error: {e} - {err_body}")
        return False, err_body
    except Exception as e:
        print(f"[USER ERROR] update_user: {e}")
        return False, "Connection error"

def get_user_info_service(user_id: int) -> tuple:
    url = f"{current_app.config['BASE_URL']}get_user_info/{user_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json().get('Data')  # ✅ capital D
        else:
            return False, response.json()

    except Exception as e:
        print(f"Error: {e} coming from get_user_info_service")
        return False, None

def create_student_service(account_id: int, form_items: list, files: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_student/{account_id}"
    try:
        upload_files = {}
        image_file = files.get("image")
        if image_file and image_file.filename:
            upload_files["image"] = (
                image_file.filename,
                image_file.stream,
                image_file.mimetype
            )

        response = requests.post(
            url,
            data=form_items,
            files=upload_files if upload_files else None,
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error: {e} coming from create_student_service")
        return False, None

def get_student_with_session_service():
    url = f"{current_app.config['BASE_URL']}get_students_with_sessions"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json().get('data')
        else:
            return False, response.json()
    except Exception as e:
        print(e)
        return False,None
