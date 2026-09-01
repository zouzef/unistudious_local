# app/account/service.py
import requests
from flask import current_app



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
