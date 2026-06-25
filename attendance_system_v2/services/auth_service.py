# services/auth_service.py

import requests
import urllib3
from utils.logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login_slc(base_url: str, mac: str, password: str) -> str | None:
    """Login to Flask server and return JWT token."""
    url = f"{base_url}/login_slc"
    try:
        response = requests.post(
            url,
            json={"mac": mac, "password": password},
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
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Flask server at {url}")
        return None
    except requests.exceptions.Timeout:
        logger.error("Login request timed out.")
        return None
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return None