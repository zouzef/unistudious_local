import requests
import json
from datetime import datetime,timedelta

with open("tablet_configuration.json", "r") as f:
    config=json.load(f)



BASE_URL=config["url"]["API_BASE_URL"]
USERNAME=config["config"]["username"]
PASSWORD=config["config"]["password"]


def login_tablet():
    url = f"{BASE_URL}/login"
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    try:
        response = requests.post(url, json=payload, verify=False, timeout=10)
        response.raise_for_status()
        login_data = response.json()
        token = login_data.get("token")
        if token:
            print(f"Successfully logged into local server. Token retrieved.")
            return token
        else:
            print("Login failed: Token not found in response.")
            return None
    except requests.RequestException as e:
        print(f"Error logging into local server at {url}: {e}")
        return None


login_tablet()
