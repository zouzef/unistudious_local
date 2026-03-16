"""Tablet-related business logic."""
import requests
import time
from datetime import datetime, timedelta
from auth.token_manager import token_manager
from utils.config import config

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


base_url = config["url"]["API_BASE_URL"]


def fetch_all_tablets():
    """Fetch all tablets from the API with retry logic."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
            endpoint = config["url"]["get_all_tablets"]
            url = f"{base_url}{endpoint}"
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
            print(f"Error fetching tablets: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None


def is_tablet_registered(tablet_id, tablets):
    """Check if tablet ID is registered."""
    for tablet in tablets:
        if tablet["mac"] == tablet_id:
            return True
    return False


def get_tablet_room(tablet_id, tablets):
    """Get room ID for a tablet."""
    for tablet in tablets:
        if tablet["mac"] == tablet_id:
            return tablet["roomId"]
    return None


def get_room_name(room_id, tablets):
    """Get room name from room ID."""
    for tablet in tablets:
        if tablet["roomId"] == room_id:
            return tablet.get("roomName", f"Room {room_id}")
    return f"Room {room_id}"


def fetch_slc_info():
    try:
        url = f"{base_url}/get_slc_id"
        response = requests.get(url,verify=False)
        response.raise_for_status()
        if response.status_code == 200:
            print("Response get_slc_id: ",response.json())
            return response.json()
        else:
            return None

    except Exception as e:
        return None


def fetch_user_profile_image(user_id):
    """Fetch user profile image from the remote server."""
    try:
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
        url = f"{base_url}/get-profile-image/{user_id}"
        response = requests.get(url, headers=headers, verify=False, stream=True)

        if response.ok:
            return response.content, response.headers.get('Content-Type', 'image/jpeg')
        else:
            return None, None

    except Exception as e:
        print(f"Error fetching profile image for user {user_id}: {e}")
        return None, None


def fech_academie_image(tablet_id):
    try:
        url = f"{base_url}/get_academie_image/{tablet_id}"
        response = requests.get(url, verify=False,stream=True)
        if response.ok:
            return response.content,response.headers.get('Content-type', 'image/jpeg')
        else:
            return None,None
    except Exception as e:
        print(f"Error fetching profile image for user {tablet_id}: {e}")
        return None, None


def authentification_teacher(data):
    try:
        url = f"{base_url}/Authentificate-Teacher"
        response = requests.post(url, json=data, verify=False)

        return {
            "body": response.json(),
            "status_code": response.status_code
        }

    except Exception as e:
        return None