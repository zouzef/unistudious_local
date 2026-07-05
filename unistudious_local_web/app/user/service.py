# app/user/service.py
import requests
from flask import current_app


def get_all_users(account_id: int) -> dict:
    """Get all users"""
    url = f"{current_app.config['BASE_URL']}get-all-users/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[USER ERROR] get_all_users: {e}")
        return {}


def get_profile_image(user_id: int):
    """Get profile image — returns (content, mimetype)"""
    url = f"{current_app.config['BASE_URL']}get-profile-image/{user_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.content, response.headers.get('Content-Type', 'image/png')
    except Exception as e:
        print(f"[USER ERROR] get_profile_image: {e}")
        return None, None

def get_account_data_service(account_id):
    try:
        url = f"{current_app.config['BASE_URL']}get_account_data/{account_id}"
        response = requests.get(url,verify=False,timeout=10)
        return response.status_code ==200,response
    except Exception as e:
        return False,None

def get_account_image_service(account_id: int):
    """Get account image — returns (content, mimetype)"""
    url = f"{current_app.config['BASE_URL']}get_account_image/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.content, response.headers.get('Content-Type', 'image/jpeg')
        return False, None, None
    except Exception as e:
        print(f"[ACCOUNT ERROR] get_account_image_service: {e}")
        return False, None, None

def update_account_service(account_id: int, data: dict, logo_file=None) -> tuple:
    """Update account — sends multipart if logo provided, JSON otherwise"""
    url = f"{current_app.config['BASE_URL']}update_account/{account_id}"
    try:
        if logo_file:
            files    = {"logoFile": (logo_file.filename, logo_file.stream, logo_file.mimetype)}
            response = requests.post(url, data=data, files=files, verify=False, timeout=10)
        else:
            response = requests.post(url, data=data, verify=False, timeout=10)

        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        print(f"[ACCOUNT ERROR] update_account_service: {e}")
        return False, {"Message": "Connection error"}
#================================ BEGIN CRUD User  ====================
def create_user_service(data: dict) -> tuple:
    """ Insert user data"""
    url = f"{current_app.config['BASE_URL']}create_user"
    try:
        response = requests.post(url,json=data,verify=False,timeout=10)
        if response.status_code == 200:
            return True,response.json()
        else:
            return False,response.json()
    except Exception as e:
        print(f"Error: {e} coming from create_user_service")
        return False,None

def update_user(user_id: int, data: dict) -> tuple:
    """Update a real user on the remote server"""
    url = f"{current_app.config['BASE_URL']}update-user/{user_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        return True, "User updated successfully"
    except requests.exceptions.HTTPError as e:
        try:
            err_body = response.json()
        except Exception:
            err_body = response.text
        print(f"[USER ERROR] update_user HTTP error: {e} - {err_body}")
        return False, err_body
    except Exception as e:
        print(f"[USER ERROR] update_user: {e}")
        return False, "Connection error"



def delete_user(user_id: int) -> tuple:
    """Delete user"""
    url = f"{current_app.config['BASE_URL']}delete-user/{user_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "User deleted successfully"
        return False, "User not deleted"
    except Exception as e:
        print(f"[USER ERROR] delete_user: {e}")
        return False, "Connection error"

def get_user_info_service(user_id: int) -> tuple:
    url = f"{current_app.config['BASE_URL']}get_user_info/{user_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json().get('Data')  # ✅ capital D
        else:
            return False, response.json()

    except Exception as e:
        print(f"Error: {e} coming from get_user_info_service")
        return False, None
#================================ END CRUD User  ================================

def update_virtual_user(user_id: int, data: dict) -> tuple:
    """Update virtual user data"""
    url = f"{current_app.config['BASE_URL']}update-virtual-user/{user_id}"
    try:
        response = requests.post(url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "Virtual user updated successfully"
        return False, "Virtual user not updated"
    except Exception as e:
        print(f"[USER ERROR] update_virtual_user: {e}")
        return False, "Connection error"

def delete_virtual_user(user_id: int) -> tuple:
    """Delete virtual user"""
    url = f"{current_app.config['BASE_URL']}delete-virtuel-user/{user_id}"
    try:
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True, "Virtual user deleted successfully"
        return False, "Virtual user not deleted"
    except Exception as e:
        print(f"[USER ERROR] delete_virtual_user: {e}")
        return False, "Connection error"

def get_manager_info_service() -> tuple:
    url=f"{current_app.config['BASE_URL']}get-manager-info"
    try:
        response=requests.get(url,verify=False)
        if response.status_code==200:
            return True,response.json()
        else:
            return False,response.json()
    except Exception as e:
        print(e)
        return False,None

def get_all_teacher_service() -> tuple:
    url=f"{current_app.config['BASE_URL']}get_all_teachers"
    try:
        response = requests.get(url,verify=False,timeout=10)
        if response.status_code == 200:
            return True,response.json()
        else:
            return False,response.json()
    except Exception as e:
        print(f"Error: {e} coming from server")
        return False,None

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



# ================================ Teacher Crud ================================
def create_teacher_service(account_id: int, form_items: list, files: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_teacher/{account_id}"
    try:
        upload_files = {}
        image_file = files.get("image")
        if image_file and image_file.filename:
            upload_files["image"] = (
                image_file.filename,
                image_file.stream,
                image_file.mimetype
            )

        response = requests.post(
            url,
            data=form_items,
            files=upload_files if upload_files else None,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()

    except Exception as e:
        print(f"Error: {e} coming from create_teacher_service")
        return False, None


# ================================ Manager Crud ================================
def create_manager_service(account_id: int, form_items: list, files: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_manager/{account_id}"
    try:
        upload_files = {}
        image_file = files.get("image")
        if image_file and image_file.filename:
            upload_files["image"] = (
                image_file.filename,
                image_file.stream,
                image_file.mimetype
            )

        response = requests.post(
            url,
            data=form_items,
            files=upload_files if upload_files else None,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()

    except Exception as e:
        print(f"Error: {e} coming from create_manager_service")
        return False, None


# ================================ Student Crud ================================
def create_student_service(account_id: int, form_items: list, files: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_student/{account_id}"
    try:
        upload_files = {}
        image_file = files.get("image")
        if image_file and image_file.filename:
            upload_files["image"] = (
                image_file.filename,
                image_file.stream,
                image_file.mimetype
            )

        response = requests.post(
            url,
            data=form_items,
            files=upload_files if upload_files else None,
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error: {e} coming from create_student_service")
        return False, None

# ================================ virtuelStudent Crud ================================
def create_virtuel_user_service(account_id: int, form_items: list) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_virtuel_user/{account_id}"
    try:
        response = requests.post(
            url,
            data=form_items,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()

    except Exception as e:
        print(f"Error: {e} coming from create_virtuel_user_service")
        return False, None
