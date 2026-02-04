import requests
import time
from datetime import datetime,timedelta
from auth.token_manager import token_manager
from utils.config import config

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = config["url"]["API_BASE_URL"]


def fetch_calender_room(room_id):
	try:
		url = f"{base_url}/get-calendar-room/{room_id}"
		response = requests.get(url,verify=False)
		response.raise_for_status()
		return response.json()
	except Exception as e:
		return None


def fetch_group_session(account_id, session_id):
	try:
		url = f"{base_url}/get-group/{account_id}/{session_id}"
		response = requests.get(url, verify=False)

		# raise_for_status() will raise an exception for 4xx/5xx status codes
		response.raise_for_status()

		# If we get here, status code is 2xx
		return response.json()

	except requests.exceptions.RequestException as e:
		# Log the error (optional but recommended)
		print(f"Error fetching group session: {e}")
		return None
	except Exception as e:
		print(f"Unexpected error: {e}")
		return None


def fetch_room(local_id):
	try:
		url = f"{base_url}/get_room/{local_id}"
		response = requests.get(url, verify=False)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		print(f"Error fetching group session: {e}")
		return None
	except Exception as e:
		print(f"Unexpected error: {e}")
		return None
