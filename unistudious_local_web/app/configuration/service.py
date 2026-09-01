import requests
from flask import current_app


# -------------------------- account services --------------------------
def get_account_level_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_account_level/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
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
		return response.status_code==200,response
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


# -------------------------- Account section --------------------------
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

def get_section_config_service():
	try:
		url = f"{current_app.config['BASE_URL']}get_section_config"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None


# -------------------------- Account Subject Service --------------------------
def get_account_subject_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_account_subject/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def delete_account_subject_service(account_subject_id):
	try:
		url = f"{current_app.config['BASE_URL']}delete_account_subject/{account_subject_id}"
		response = requests.post(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def get_subject_service():
	try:
		url = f"{current_app.config['BASE_URL']}get_subject_config"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def create_subject_config_service(data,account_id):
	try:
		url = f"{current_app.config['BASE_URL']}create_account_subject/{account_id}"
		response = requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		print(e)
		return False,None

def update_subject_config_service(data,account_subject_id):
	try:
		url = f"{current_app.config['BASE_URL']}update_account_subject/{account_subject_id}"
		response = requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response

	except Exception as e:
		return False,None

def view_account_subject_service(account_subject_id):
	try:
		url = f"{current_app.config['BASE_URL']}view_account_subject/{account_subject_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code==200,response
	except Exception as e:
		return False,None


# -------------------------- Formation Service --------------------------




# -------------------------- Tag Service --------------------------
def get_all_tag_service():
	try:
		url = f"{current_app.config['BASE_URL']}get_all_tag"
		response= requests.get(url,verify=False,timeout=10)
		return response.status_code==200,response
	except Exception as e:
		return False,None

def get_all_subject_config_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_account_tag/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def delete_account_tag_service(account_tag_id):
	try:
		url = f"{current_app.config['BASE_URL']}delete_account_tag/{account_tag_id}"
		response = requests.post(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def get_account_tag_service(account_tag_id):
	try:
		url =f"{current_app.config['BASE_URL']}view_account_tag/{account_tag_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200 ,response
	except Exception as e:
		return False,None

def update_account_tag_service(account_tag_id, data):
	try:
		url = f"{current_app.config['BASE_URL']}edit_account_tag/{account_tag_id}"
		response= requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response


	except Exception as e:
		return False,None

def create_account_tag_service(account_id, data):
	try:
		url =f"{current_app.config['BASE_URL']}create_account_tag/{account_id}"
		response = requests.post(url, json=data, verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		print(e)
		return False,None


# -------------------------- Completion tag Service --------------------------
def get_all_completion_tag_serice(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_all_completion_tag/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def create_completion_tag_service(account_id,data):
	try:
		url =f"{current_app.config['BASE_URL']}create_completion_tag/{account_id}"
		response = requests.post(url, json=data, verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def view_completion_tag_service(completionTagId):
	try:
		url = f"{current_app.config['BASE_URL']}view_completion_tag/{completionTagId}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None

def update_completion_tag_service(completonTagId,data):
	try:
		url = f"{current_app.config['BASE_URL']}update_completion_tag/{completonTagId}"
		response = requests.post(url,json=data,verify=False,timeout=10)
		return response.status_code == 200,response

	except Exception as e:
		return False,None

def delete_completion_tag_service(completionTagId):
	try:
		url = f"{current_app.config['BASE_URL']}delete_completion_tag/{completionTagId}"
		response = requests.post(url,verify=False,timeout=10)
		return response.status_code == 200,response
	except Exception as e:
		return False,None


# -------------------------- Door Service --------------------------
def get_all_door_service():
	try:
		url = f"{current_app.config['BASE_URL']}get_all_door"
		response = requests.get(url, verify=False, timeout=10)
		return response.status_code == 200, response
	except Exception as e:
		return False,None

def create_door_service(data):
	try:
		url = f"{current_app.config['BASE_URL']}create_door"
		response = requests.post(url,json=data, verify=False, timeout=10)
		return response.status_code == 200, response
	except Exception as e:
		return False,None

def delete_door_service(door_id):
	try:
		url = f"{current_app.config['BASE_URL']}delete_door/{door_id}"
		response = requests.post(url,verify=False, timeout=10)
		return response.status_code == 200, response
	except Exception as e:
		return False,None

def update_door_service(door_id, payload):
	try:
		url = f"{current_app.config['BASE_URL']}update_door/{door_id}"
		response = requests.post(url,json=payload,verify=False,timeout=10)
		return response.status_code == 200, response
	except Exception as e:
		return False,None

def view_door_service(door_id):
	try:
		url = f"{current_app.config['BASE_URL']}view_detail_door/{door_id}"
		response = requests.get(url,verify=False,timeout=10)
		return response.status_code == 200, response
	except Exception as e:
		return False,None