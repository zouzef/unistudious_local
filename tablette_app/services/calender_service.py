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