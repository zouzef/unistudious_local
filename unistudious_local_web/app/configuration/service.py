import requests
from flask import current_app



def get_account_level_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_account_level/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		print(response.json())
		return response.status_code == 200,response
	except Exception as e:
		print(e)
		return False,None

def create_account_level_service(data,account_id):
	try:
		url = f"{current_app.config['BASE_URL']}create_account_level/{account_id}"
		response = requests.post(url,json=data,verify=False)
		return response.status_code == 200,response
	except Exception as e:
		print(e)
		return False,None

def delete_account_level_service(account_id,account_level_id):
	try:
		url = f"{current_app.config['BASE_URL']}delete_account_level/{account_id}/{account_level_id}"
		response = requests.post(url,verify=False,timeout=10)
		return response.status_code==200,response.status_code
	except Exception as e:
		return False,None

def view_account_level_service(account_level_id):
	try:
		url = f"{current_app.config['BASE_URL']}view_account_level/{account_level_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def update_account_level_servie(data,account_level_id):
	try:
		url = f"{current_app.config['BASE_URL']}edit_account_level/{account_level_id}"
		response = requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response

	except Exception as e:
		return False,None

def get_level_service():
	try:
		url = f"{current_app.config['BASE_URL']}get_all_level"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code==200,response
	except Exception as e:
		print(f"Error: {e}")
		return False,None



def get_account_section_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_account_section/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def create_account_section_service(data,account_id):
	try:
		url = f"{current_app.config['BASE_URL']}create_account_section/{account_id}"
		response = requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def delete_account_section_service(account_section_id):
	try:
		url = f"{current_app.config['BASE_URL']}delete_account_section/{account_section_id}"
		response = requests.post(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def update_account_section_service(data,account_section_id):
	try:
		url = f"{current_app.config['BASE_URL']}update_account_section/{account_section_id}"
		response = requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response

	except Exception as e:
		return False,None

def view_account_section_service(account_section_id):
	try:
		url=f"{current_app.config['BASE_URL']}view_account_section/{account_section_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response

	except Exception as e:
		return False,None