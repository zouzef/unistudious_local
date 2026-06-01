# app/session/service.py
import requests
from flask import current_app
from app.utils.auth import auth_headers

def get_all_sessions(account_id: int) -> list:
    url = f"{current_app.config['BASE_URL']}get_session_detail/{account_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_all_sessions: {e}")
        return []


def get_moderator(account_id: int) -> dict:
    url = f"{current_app.config['BASE_URL']}get_data_moderateur/{account_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', {})
    except Exception as e:
        print(f"[SESSION ERROR] get_moderator: {e}")
        return {}


def get_locals(account_id: int) -> list:
    url = f"{current_app.config['BASE_URL']}get_local_detail/{account_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_locals: {e}")
        return []


def get_room(local_id: int) -> list:
    url = f"{current_app.config['BASE_URL']}get_room/{local_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_room: {e}")
        return []


def get_teacher(session_id: int) -> list:
    url = f"{current_app.config['BASE_URL']}get_teacher_session/{session_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_teacher: {e}")
        return []


def get_session_image(session_id: int):
    url = f"{current_app.config['BASE_URL']}get_session_image/{session_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        return response.content, response.headers.get('Content-Type', 'image/png')
    except Exception as e:
        print(f"[SESSION ERROR] get_session_image: {e}")
        return None, None


def create_session_local(session_data):
    url = f"{current_app.config['BASE_URL']}create-session"
    try:
        response = requests.post(url, headers=auth_headers(), json=session_data, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, 200
        else:
            return False, 400
    except Exception as e:
        print(f"Error in create_session service: {e}")
        return False, 500


def get_session_info_service(session_id):
    url = f"{current_app.config['BASE_URL']}get_session_info/{session_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except Exception as e:
        return False, None


def update_session_service(session_data, session_id):
    url = f"{current_app.config['BASE_URL']}update_session/{session_id}"
    try:
        response = requests.post(url, headers=auth_headers(), json=session_data, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"❌ Service error: {e}")
        return False, None


def delete_session_service(session_id):
    url = f"{current_app.config['BASE_URL']}delete_session/{session_id}"
    try:
        response = requests.post(url, headers=auth_headers(), verify=False, timeout=10)
        if response.status_code == 200:
            return True, {"nbrgroup": response.json()}
        else:
            return False, {"nbrgroup": response.json()}
    except Exception as e:
        return False, None


def get_all_user_service(session_id):
    url = f"{current_app.config['BASE_URL']}get_all_user_session/{session_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        if response.status_code == 200:
            return True, {"nbruser": response.json()}
        else:
            return False, {"nbruser": response.json()}
    except Exception as e:
        print(f"Error: {e} in get_all_user_service")
        return False, None


def get_all_group_session_service(session_id):
    url = f"{current_app.config['BASE_URL']}get_all_group_session/{session_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error: {e} in get nb group session")
        return False, None


def get_user_info_session_service(session_id):
    url = f"{current_app.config['BASE_URL']}get_user_session_info/{session_id}"
    try:
        response = requests.get(url, headers=auth_headers(), verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error:{e} coming from get_user_info_session")
        return False, None


def delete_user_session_service(session_id, user_id):
    url = f"{current_app.config['BASE_URL']}delete_relation_user_session/{user_id}/{session_id}"
    try:
        response = requests.post(url, headers=auth_headers(), verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, None