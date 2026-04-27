# app/session/service.py
import requests
import os
import io
import base64
from flask import current_app


def get_all_sessions(account_id: int) -> list:
    """Get all sessions"""
    url = f"{current_app.config['BASE_URL']}get_session_detail/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_all_sessions: {e}")
        return []


def get_moderator(account_id: int) -> dict:
    """Get moderator data"""
    url = f"{current_app.config['BASE_URL']}get_data_moderateur/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', {})
    except Exception as e:
        print(f"[SESSION ERROR] get_moderator: {e}")
        return {}


def get_locals(account_id: int) -> list:
    """Get local details"""
    url = f"{current_app.config['BASE_URL']}get_local_detail/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_locals: {e}")
        return []


def get_room(local_id: int) -> list:
    """Get rooms from local"""
    url = f"{current_app.config['BASE_URL']}get_room/{local_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_room: {e}")
        return []


def get_teacher(session_id: int) -> list:
    """Get teachers from session"""
    url = f"{current_app.config['BASE_URL']}get_teacher_session/{session_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"[SESSION ERROR] get_teacher: {e}")
        return []


def get_session_image(session_id: int):
    """Get session image — returns (content, mimetype)"""
    url = f"{current_app.config['BASE_URL']}get_session_image/{session_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.content, response.headers.get('Content-Type', 'image/png')
    except Exception as e:
        print(f"[SESSION ERROR] get_session_image: {e}")
        return None, None


def create_session_local(session_data):
    url = f"{current_app.config['BASE_URL']}create-session"
    try:
        response = requests.post(url, json=session_data, verify=False, timeout=10)
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
        response=  requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True,response.json()
        else:
            return False,None

    except Exception as e:
        return False,None
