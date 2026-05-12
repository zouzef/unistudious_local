# app/payments/service.py
import requests
from flask import current_app



def get_paymet_session_service(session_id: int) -> tuple:
	url = f"{current_app.config['BASE_URL']}get_payment_session/{session_id}"
	try:
		response = requests.get(url,verify=False,timeout=10)
		if response.status_code == 200:
			return True,response.json()
		else:
			return False,response.json()

	except Exception as e:
		print(f"Error: {e} coming from server!")
		return False,None


def get_payment_user_info_service(user_id: int,session_id: int) -> tuple:
    try:
        url = f"{current_app.config['BASE_URL']}get_payment_session_user/{session_id}/{user_id}"
        response = requests.get(url,verify=False,timeout=10)
        if response.status_code == 200:
            return True,response.json()
        else:
            return False,response.json()

    except Exception as e:
        return False,None


def update_payment_service(payment_session_id: int, data) -> tuple:
    try:
        url = f"{current_app.config['BASE_URL']}update_payment_session/{payment_session_id}"
        response = requests.post(url, verify=False,json=data, timeout=10)
        if response.status_code == 200:  # ✅ no parentheses
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error: {e} coming from update_payment_service")
        return False, None


def update_payment_user_service(payment_id, session_id,user_id,data):
	url=f"{current_app.config['BASE_URL']}update_payment_session_user/{session_id}/{user_id}/{payment_id}"
	try:
		response = requests.post(url,json=data,verify=False)
		print("response data: ",response.json())
		if response.status_code == 200:
			return True,response.json()
		else:
			return False,response.json()

	except Exception as e:
		print(f"Error: {e} coming from update_payment_user_service ")
		return False,None