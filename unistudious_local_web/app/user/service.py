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
    """Update user data"""
    url = f"{current_app.config['BASE_URL']}update-user/{user_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "User updated successfully"
        return False, response.json()
    except Exception as e:
        print(f"[USER ERROR] update_user: {e}")
        return False, "Connection error"


def delete_user(user_id: int) -> tuple:
    """Delete user"""
    url = f"{current_app.config['BASE_URL']}delete-user/{user_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "User deleted successfully"
        return False, "User not deleted"
    except Exception as e:
        print(f"[USER ERROR] delete_user: {e}")
        return False, "Connection error"


def update_virtual_user(user_id: int, data: dict) -> tuple:
    """Update virtual user data"""
    url = f"{current_app.config['BASE_URL']}update-virtual-user/{user_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "Virtual user updated successfully"
        return False, "Virtual user not updated"
    except Exception as e:
        print(f"[USER ERROR] update_virtual_user: {e}")
        return False, "Connection error"


def delete_virtual_user(user_id: int) -> tuple:
    """Delete virtual user"""
    url = f"{current_app.config['BASE_URL']}delete-virtuel-user/{user_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "Virtual user deleted successfully"
        return False, "Virtual user not deleted"
    except Exception as e:
        print(f"[USER ERROR] delete_virtual_user: {e}")
        return False, "Connection error"


def get_manager_info_service():
    url=f"{current_app.config['BASE_URL']}/get-manager-info"
    try:
        response=requests.get(url,verify=False)
        if response.staus_code==200:
            return True,response.json()
        else:
            return False,response.json()
    except Exception as e:
        print(e)
        return False,None