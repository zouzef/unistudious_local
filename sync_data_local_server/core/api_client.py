"""
API Client for remote server communication
Handles authenticated HTTP requests with automatic token refresh
"""
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auth import get_token, handle_unauthorized


class APIClient:
    """Handles all API communication with the remote server"""

    def __init__(self, settings):
        """
        Initialize API Client

        Args:
            settings: Settings instance with API configuration
        """
        self.settings = settings
        self.base_url = settings.api_base_url
        self.timeout = settings.api_timeout

    def _get_headers(self):
        """
        Get headers with authentication token

        Returns:
            dict: Request headers with auth token
        """
        token = get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response):
        """
        Handle API response and check for errors

        Args:
            response: requests.Response object

        Returns:
            dict: Response data as JSON

        Raises:
            Exception: If request failed
        """
        # Handle token expiration
        if response.status_code == 401:
            print("⚠️  Token expired, refreshing...")
            new_token = handle_unauthorized()
            if new_token:
                raise TokenExpiredError("Token refreshed, retry request")
            else:
                raise Exception("Failed to refresh token")

        # Handle other errors
        if response.status_code != 200:
            raise Exception(
                f"API request failed with status {response.status_code}: {response.text}"
            )

        return response.json()

    def _request_with_retry(self, method, url, **kwargs):
        """
        Make HTTP request with automatic retry on token expiration

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL
            **kwargs: Additional request parameters

        Returns:
            dict: Response data
        """
        max_retries = 2
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Get fresh headers (with current token)
                kwargs['headers'] = self._get_headers()
                kwargs['timeout'] = self.timeout

                # Make request
                response = requests.request(method, url, **kwargs)
                return self._handle_response(response)

            except TokenExpiredError:
                # Token was refreshed, retry the request
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception("Max retries reached after token refresh")
                print(f"🔄 Retrying request (attempt {retry_count}/{max_retries})...")
                continue

            except requests.RequestException as e:
                print(f"❌ Network error: {e}")
                raise

    def get(self, endpoint):
        """
        Make GET request to API

        Args:
            endpoint: API endpoint (e.g., '/api/data')

        Returns:
            dict: Response data
        """
        url = f"{self.base_url}{endpoint}"
        print(f"📡 GET {url}")
        return self._request_with_retry("GET", url)

    def post(self, endpoint, data=None):
        """
        Make POST request to API

        Args:
            endpoint: API endpoint
            data: Data to send in request body

        Returns:
            dict: Response data
        """
        url = f"{self.base_url}{endpoint}"
        print(f"📡 POST {url}")
        return self._request_with_retry("POST", url, json=data)

    def fetch_whats_new(self):
        """
        Fetch latest updates from the 'whats new' endpoint

        Returns:
            dict: Latest data from remote server
        """
        print("🔄 Fetching latest data from remote server...")
        endpoint = self.settings.config['api']['whats_new_endpoint']
        return self.post(endpoint)


class TokenExpiredError(Exception):
    """Custom exception for token expiration"""
    pass


