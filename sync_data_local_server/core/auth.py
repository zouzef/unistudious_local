"""
Authentication and token management - Function-based approach
"""
import requests
import threading
import time
from datetime import datetime


# Global token storage
_current_token = None
_token_lock = threading.Lock()
_refresh_thread = None
_stop_refresh = False
_settings = None


def init_auth(settings):
    """
    Initialize auth module with settings

    Args:
        settings: Settings instance
    """
    global _settings, _current_token
    _settings = settings

    # Try to load existing token
    _current_token = settings.get_token()


def get_token():
    """
    Get current valid token (requests new one if not available)

    Returns:
        str: Valid authentication token
    """
    global _current_token, _settings

    if _settings is None:
        raise RuntimeError("Auth not initialized. Call init_auth(settings) first")

    with _token_lock:
        if not _current_token:
            print("⚠️  No token available, requesting new token...")
            _current_token = request_new_token()

        return _current_token


def request_new_token():
    """
    Request a new token from the authentication API

    Returns:
        str: New authentication token

    Raises:
        Exception: If authentication fails
    """
    global _settings

    if _settings is None:
        raise RuntimeError("Auth not initialized. Call init_auth(settings) first")

    try:
        print(f"🔐 Authenticating user: {_settings.username}")

        payload = {
            "username": _settings.username,
            "password": _settings.password
        }

        response = requests.post(
            _settings.login_url,
            json=payload,
            timeout=_settings.api_timeout
        )

        # Check for errors
        if response.status_code != 200:
            raise Exception(
                f"Authentication failed with status {response.status_code}: {response.text}"
            )

        # Extract token
        data = response.json()
        token = data.get("token")

        if not token:
            raise Exception("No token received from authentication API")

        print("✅ Authentication successful")

        # Save token to config
        _settings.set_token(token)

        return token

    except requests.RequestException as e:
        print(f"❌ Network error during authentication: {e}")
        raise
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        raise


def refresh_token():
    """
    Refresh the authentication token

    Returns:
        bool: True if refresh successful, False otherwise
    """
    global _current_token

    with _token_lock:
        try:
            print(f"🔄 Refreshing token at {datetime.now()}")
            _current_token = request_new_token()
            return True
        except Exception as e:
            print(f"❌ Failed to refresh token: {e}")
            return False


def handle_unauthorized():
    """
    Handle 401 Unauthorized response by refreshing token

    Returns:
        str: New token or None if refresh failed
    """
    print("⚠️  Received 401 Unauthorized - Token expired")
    if refresh_token():
        return get_token()
    return None


def start_auto_refresh():
    """Start background thread for automatic token refresh"""
    global _refresh_thread, _stop_refresh, _settings

    if _settings is None:
        raise RuntimeError("Auth not initialized. Call init_auth(settings) first")

    if _refresh_thread and _refresh_thread.is_alive():
        print("⚠️  Auto-refresh already running")
        return

    _stop_refresh = False
    _refresh_thread = threading.Thread(
        target=_auto_refresh_loop,
        daemon=True
    )
    _refresh_thread.start()

    interval = _settings.token_refresh_interval_minutes
    print(f"✅ Auto-refresh started (every {interval} minutes)")


def stop_auto_refresh():
    """Stop the automatic token refresh thread"""
    global _stop_refresh, _refresh_thread

    _stop_refresh = True
    if _refresh_thread:
        _refresh_thread.join(timeout=5)
    print("✅ Auto-refresh stopped")


def _auto_refresh_loop():
    """Background loop that refreshes token periodically"""
    global _settings

    while not _stop_refresh:
        try:
            interval = _settings.token_refresh_interval_minutes
            time.sleep(interval * 60)

            if not _stop_refresh:
                refresh_token()
        except Exception as e:
            print(f"❌ Error in auto-refresh loop: {e}")
