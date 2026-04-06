"""Tablet-related business logic."""
import requests
import time
from datetime import datetime, timedelta
from auth.token_manager import token_manager
from utils.config import config

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


base_url = config["url"]["API_BASE_URL"]

def fetch_subject():
    try:
        url = f"{base_url}/get_sub_subjects"
        response = requests.get(url,verify=False)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json().get("data")
            return data
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None