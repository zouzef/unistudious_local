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