"""
Data fetcher for remote server synchronization
Handles API calls to fetch updated data from remote server
"""
import requests
from datetime import timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.api_client import APIClient, TokenExpiredError


class DataFetcher:
    """Fetches data from remote server with date filtering"""

    def __init__(self, settings):
        """
        Initialize DataFetcher

        Args:
            settings: Settings instance
        """
        self.settings = settings
        self.api_client = APIClient(settings)
        self.whats_new_endpoint = settings.config['api']['whats_new_endpoint']

    def fetch_data(self, since_date=None):
        """
        Fetch data from remote server

        Args:
            since_date: Optional datetime to fetch only changes since this date

        Returns:
            dict: Server response containing created/updated data
        """
        try:
            print(f"\n🔄 Fetching data from remote server...")

            # Prepare payload
            payload = {}

            if since_date:
                # Adjust date by subtracting 1 hour (as in original code)
                adjusted_date = since_date - timedelta(hours=1)
                date_str = adjusted_date.strftime("%Y-%m-%d %H:%M")
                payload['date'] = date_str
                print(f"📅 Fetching changes since: {date_str}")
            else:
                print("📅 Fetching all data (full sync)")

            # Make request using APIClient (handles token refresh automatically)
            # Note: APIClient.post() sends as JSON, but the original code sends as form data
            # We need to modify the request to send as form data
            data = self._post_with_form_data(self.whats_new_endpoint, payload)

            print("✅ Data fetched successfully")
            return data

        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            raise

    def _post_with_form_data(self, endpoint, data=None):
        """
        Make POST request with form data (not JSON)
        This matches the original code's behavior

        Args:
            endpoint: API endpoint
            data: Data to send as form data

        Returns:
            dict: Response data
        """
        url = f"{self.settings.api_base_url}{endpoint}"
        print(f"📡 POST {url}")

        max_retries = 2
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Get headers with current token
                from core.auth import get_token, handle_unauthorized
                token = get_token()

                headers = {
                    "Authorization": f"Bearer {token}"
                }

                # Make request with form data (not JSON)
                response = requests.post(
                    url,
                    headers=headers,
                    data=data,  # Send as form data, not JSON
                    timeout=self.settings.api_timeout
                )

                # Check for token expiration
                if response.status_code == 401 or "token expired" in response.text.lower():
                    print("⚠️  Token expired, refreshing...")
                    new_token = handle_unauthorized()

                    if new_token:
                        retry_count += 1
                        if retry_count >= max_retries:
                            raise Exception("Max retries reached after token refresh")
                        print(f"🔄 Retrying request (attempt {retry_count}/{max_retries})...")
                        continue
                    else:
                        raise Exception("Failed to refresh token")

                # Check for other errors
                response.raise_for_status()

                return response.json()

            except requests.RequestException as e:
                print(f"❌ Network error: {e}")
                raise

    def has_new_data(self, data):
        """
        Check if the API response contains any new data

        Args:
            data: API response dictionary

        Returns:
            bool: True if there's new data, False otherwise
        """
        if not data:
            return False

        # List of all data sections to check
        data_keys = [
            "user", "account", "local_with_room", "subject", "accountSubject",
            "attendance", "session", "relationUserSession", "calendar", "group",
            "relationTeacherAndSubjectData", "admin", "slcTablet", "slcLocal",
            "slc", "slcCamera", "formation"
        ]

        for key in data_keys:
            section = data.get(key, {})

            # Check if section is a dict with created/updated
            if isinstance(section, dict):
                if section.get("created") or section.get("updated"):
                    print(f"✅ Found new data in: {key}")
                    return True

            # Check if section is a non-empty list
            elif isinstance(section, list) and section:
                print(f"✅ Found new data in: {key} (list)")
                return True

        print("ℹ️  No new data found")
        return False

