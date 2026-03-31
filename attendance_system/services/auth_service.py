# services/auth_service.py

import requests
import urllib3
from utils.logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login_slc(base_url: str, username: str, password: str) -> str | None:
    """Login to Flask server and return token."""
    url = f"{base_url}/auth/login"
    try:
        response = requests.post(
            url,
            json={"username": username, "password": password},
            verify=False,
            timeout=10
        )
        response.raise_for_status()
        token = response.json().get("token")
        if token:
            logger.info("Login successful.")
            return token
        logger.error("Login response missing token.")
        return None
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return None