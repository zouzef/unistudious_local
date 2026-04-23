# app/formation/service.py
import requests
from flask import current_app
from datetime import datetime


# Service: Get formation info
def fetch_formation_info(account_id):
    url = f"{current_app.config['BASE_URL']}get-formation-info/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None