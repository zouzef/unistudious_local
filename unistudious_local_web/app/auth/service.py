# app/auth/service.py  (PLATFORM BACKEND)
# ─────────────────────────────────────────────────────────────────────────────
# All calls to the local API server now attach the JWT as a Bearer token.
# The token lives in the Flask session after login.
# ─────────────────────────────────────────────────────────────────────────────
import requests
from flask import current_app, session


def _auth_headers() -> dict:
    """
    Build the Authorization header from the token stored in the session.
    Every service function that calls the local API server uses this.
    """
    token = session.get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def login(username: str, password: str) -> tuple:
    """
    Authenticate against the local API server.
    Returns (success, user_data, message).
    Note: no token header needed here — this IS the login call.
    """
    if not username or not username.strip():
        return False, None, "Username is required"
    if not password:
        return False, None, "Password is required"

    url     = f"{current_app.config['BASE_URL']}authentification-moderateur"
    payload = {"username": username.strip(), "password": password}

    try:
        response = requests.post(
            url,
            json=payload,
            verify=current_app.config['VERIFY_SSL'],
            timeout=current_app.config['REQUEST_TIMEOUT'],
        )

        if response.status_code == 200:
            data = response.json()
            session["access_token"] = data.get("access_token")  # ← ADD
            session["account_id"] = data.get("account_id")  # ← ADD
            print(f"[DEBUG] full API response: {data}")  # ← ADD THIS
            print(f"[DEBUG] token from API: {data.get('access_token')}")
            user_data = {
                "user_id": data.get("user_id"),
                "account_id": data.get("account_id"),
                "username": username.strip(),
                "access_token": data.get("access_token"),
            }
            return True, user_data, "Login successful"
        elif response.status_code == 401:
            return False, None, "Invalid username or password"
        elif response.status_code == 403:
            return False, None, "Access denied: insufficient permissions"
        elif response.status_code == 400:
            return False, None, "Bad request — missing credentials"
        else:
            return False, None, "Authentication service error"

    except requests.exceptions.ConnectionError:
        return False, None, "Cannot reach the authentication server"
    except requests.exceptions.Timeout:
        return False, None, "Authentication server timed out"
    except requests.exceptions.RequestException as e:
        print(f"[AUTH SERVICE] Unexpected error: {e}")
        return False, None, "Connection error"


# ─────────────────────────────────────────────────────────────────────────────
# All functions below attach the Bearer token automatically via _auth_headers()
# ─────────────────────────────────────────────────────────────────────────────

def get_dashboard_data(account_id: int) -> tuple:
    """Returns (success, data, message)"""
    url = f"{current_app.config['BASE_URL']}get_data_moderateur/{account_id}"
    try:
        response = requests.get(
            url,
            headers=_auth_headers(),
            verify=current_app.config['VERIFY_SSL'],
            timeout=current_app.config['REQUEST_TIMEOUT'],
        )
        if response.status_code == 200:
            return True, response.json().get("data"), "OK"
        elif response.status_code == 401:
            return False, None, "Session expired — please log in again"
        else:
            return False, None, "Failed to load dashboard data"
    except requests.exceptions.RequestException as e:
        print(f"[SERVICE] get_dashboard_data error: {e}")
        return False, None, "Connection error"


def get_account_data(account_id: int) -> tuple:
    """Returns (success, data, message)"""
    url = f"{current_app.config['BASE_URL']}get_account_data/{account_id}"
    try:
        response = requests.get(
            url,
            headers=_auth_headers(),
            verify=current_app.config['VERIFY_SSL'],
            timeout=current_app.config['REQUEST_TIMEOUT'],
        )
        if response.status_code == 200:
            return True, response.json(), "OK"
        elif response.status_code == 401:
            return False, None, "Session expired — please log in again"
        elif response.status_code == 404:
            return False, None, "Account not found"
        else:
            return False, None, "Failed to load account data"
    except requests.exceptions.RequestException as e:
        print(f"[SERVICE] get_account_data error: {e}")
        return False, None, "Connection error"


def update_account(account_id: int, name: str, status: str, logo=None) -> tuple:
    """Returns (success, message)"""
    url  = f"{current_app.config['BASE_URL']}update_account/{account_id}"
    form = {"name": name, "status": status}
    files = {"logoFile": logo} if logo else None
    try:
        response = requests.post(
            url,
            headers=_auth_headers(),
            data=form,
            files=files,
            verify=current_app.config['VERIFY_SSL'],
            timeout=current_app.config['REQUEST_TIMEOUT'],
        )
        if response.status_code == 200:
            return True, "Account updated successfully"
        elif response.status_code == 401:
            return False, "Session expired — please log in again"
        elif response.status_code == 404:
            return False, "Account not found"
        else:
            return False, response.json().get("Message", "Update failed")
    except requests.exceptions.RequestException as e:
        print(f"[SERVICE] update_account error: {e}")
        return False, "Connection error"