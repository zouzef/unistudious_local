# app/formation/service.py
import requests
from flask import current_app,Response
from datetime import datetime



# Service: Get formation info
def fetch_formation_info(account_id):
    url = f"{current_app.config['BASE_URL']}get-formation-info/{account_id}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

# Service: Create formation Service
def create_formation_service(account_id, data, files=None):
    url = f"{current_app.config['BASE_URL']}create_formation/{account_id}"
    try:
        response = requests.post(
            url,
            verify=False,
            data=data,
            files=files,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()

    except requests.exceptions.RequestException as e:
        print(f"Create_formation_service error: {e}")
        return False, None

def get_all_foramtion_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get-formation-info/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code==200,response
	except Exception as e:
		return False,None

def delete_formation_service(formation_id,account_id):
	try:
		url =f"{current_app.config['BASE_URL']}delete_formation/{formation_id}/{account_id}"
		response = requests.post(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def view_formation_service(formation_id):
	try:
		url = f"{current_app.config['BASE_URL']}view_formation/{formation_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def update_formation_service(formation_id,data):
	try:
		url=f"{current_app.config['BASE_URL']}update_formation/{formation_id}"
		print(url)
		response = requests.get(url,
								 json=data,
								 verify=False,
								timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def get_formation_image_service(formation_id):
	url = f"{current_app.config['BASE_URL']}get_formation_image/{formation_id}"
	try:
		response = requests.get(url, timeout=10, verify=False)
		if response.status_code != 200:
			return False, None, None

		return True, response.content, response.headers.get('Content-Type', 'image/jpeg')
	except Exception as e:
		print(e)
		return False, None, None


def view_formation_image(formation_id):
	try:
		query = """
			DELETE * 
			FROM formation 
			WHERE id = %s 
		"""
		result = Database.execute_query(query,(formation_id,))
	except Exception as e:
		return False,None