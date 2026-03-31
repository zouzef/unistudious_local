# services/client.py

import requests
import urllib3
from utils.logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlaskClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False
        self._set_token(token)

    def _set_token(self, token: str):
        """Update the auth token in session headers."""
        self.token = token
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })

    def refresh_token(self, new_token: str):
        """Call this when you get a new token after re-login."""
        logger.info("Refreshing client token...")
        self._set_token(new_token)

    def get(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            logger.debug(f"GET {url}")
            response = self.session.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Flask server at {url}")
            raise
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out: GET {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error on GET {url}: {e.response.status_code}")
            raise

    def post(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            logger.debug(f"POST {url}")
            response = self.session.post(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Flask server at {url}")
            raise
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out: POST {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error on POST {url}: {e.response.status_code}")
            raise