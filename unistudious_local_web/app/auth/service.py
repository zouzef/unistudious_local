# app/auth/service.py
import requests
from flask import current_app


def login(username: str, password: str) -> tuple:
    """
    Handle login logic
    Returns (success, user_data, message)
    """

    # 1. Validate inputs
    if not username or not password:
        return False, None, "Username and password required"

    # 2. Call the API
    url = f"{current_app.config['BASE_URL']}authentification-moderateur"
    payload = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(
            url,
            json=payload,
            verify=current_app.config['VERIFY_SSL'],
            timeout=current_app.config['REQUEST_TIMEOUT']
        )

        # 3. Apply business logic
        if response.status_code == 200:
            data = response.json()
            user_data = {
                "user_id":    data.get("user_id"),
                "account_id": data.get("account_id", 3),
                "username":   username
            }
            return True, user_data, "Login successful"
        else:
            return False, None, "Invalid credentials"

    except requests.exceptions.RequestException as e:
        print(f"[AUTH ERROR] {e}")
        return False, None, "Connection error"