"""Token management and authentication."""
import threading
import time
from datetime import datetime
from login import login_tablet


class TokenManager:
    """Manages API authentication tokens with automatic refresh."""

    def __init__(self):
        self.token = None
        self.token_lock = threading.Lock()
        self._refresh_thread = None

    def initialize(self):
        """Initialize token and start refresh loop."""
        self.token = login_tablet()
        print(f"✅ Initial token loaded at {datetime.now()}")
        self._start_refresh_loop()
        return self.token

    def get_token(self):
        """Get current token (thread-safe)."""
        with self.token_lock:
            return self.token

    def refresh_token(self):
        """Refresh the authentication token."""
        try:
            print(f"🔄 Refreshing token at {datetime.now()}")
            new_token = login_tablet()
            with self.token_lock:
                self.token = new_token
            print("✅ Token refreshed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to refresh token: {e}")
            return False

    def _token_refresh_loop(self):
        """Background loop for token refresh."""
        while True:
            time.sleep(45 * 60)
            success = self.refresh_token()
            if not success:
                print("⚠️ Token refresh failed, retrying in 60s")
                time.sleep(60)
                self.refresh_token()

    def _start_refresh_loop(self):
        """Start background token refresh thread."""
        self._refresh_thread = threading.Thread(
            target=self._token_refresh_loop,
            daemon=True
        )
        self._refresh_thread.start()


# Global token manager instance
token_manager = TokenManager()