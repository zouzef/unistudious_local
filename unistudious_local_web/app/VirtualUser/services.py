import requests
from flask import current_app


# ── Create Virtuel Student service─────────────────────────────────────────────────────────────
def create_virtuel_user_service(account_id: int, form_data: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_virtuel_user/{account_id}"
    try:
        response = requests.post(
            url,
            data=form_data,
            verify=False,
            timeout=10
        )

        try:
            body = response.json()
        except ValueError:
            body = {"Message": "Invalid response from server"}

        if response.status_code == 200:
            return True, body
        return False, body

    except Exception as e:
        print(f"Error: {e} coming from create_virtuel_user_service")
        return False, {"Message": "Connection error"}

# ── Update Virtuel Student service─────────────────────────────────────────────────────────────
def update_virtual_student(vu_id: int, user_id: int, data: dict, account_id: int) -> tuple:
    """Update (or create) a virtual student on the remote server.

    NOTE: the remote Symfony endpoint reads via $request->request->get(),
    i.e. form-encoded POST data — NOT JSON.
    """
    url = f"{current_app.config['BASE_URL']}update-virtual-student/{account_id}"

    payload = {
        'userId': user_id,   # linked REAL user id
        'id':     vu_id,     # virtual_user row id
        'name':   data.get('name'),
        'phone':  data.get('phone'),
        'email':  data.get('email'),
        'status': data.get('status'),
    }

    try:
        response = requests.post(url, data=payload, verify=False, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('success'):
            return True, result.get('student')
        return False, result.get('message', 'Update failed')
    except requests.exceptions.HTTPError as e:
        try:
            err_body = response.json()
        except Exception:
            err_body = response.text
        print(f"[USER ERROR] update_virtual_student HTTP error: {e} - {err_body}")
        return False, err_body
    except Exception as e:
        print(f"[USER ERROR] update_virtual_student: {e}")
        return False, "Connection error"


# ── Delete Virtuel Student service ─────────────────────────────────────────────────────────────
def delete_virtual_user_service(user_id: int, account_id, virtual_id) -> tuple:
    """Delete virtual user"""
    url = f"{current_app.config['BASE_URL']}delete-virtuel-user/{virtual_id}"
    payload = {
        "userId": user_id,
        "account_id": account_id,
        "id": virtual_id
    }
    try:
        response = requests.post(url, json=payload, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "Virtual user deleted successfully"
        return False, "Virtual user not deleted"
    except Exception as e:
        print(f"[USER ERROR] delete_virtual_user: {e}")
        return False, "Connection error"

