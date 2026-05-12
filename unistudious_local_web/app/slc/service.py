import requests
import os
import base64
from flask import current_app


def get_slc_info_service(account_id: int) -> tuple:
	""" GET slc_info"""
	url = f"{current_app.config['BASE_URL']}get_local_detail/{account_id}"
	try:
		response = requests.get(url,verify=False,timeout=10)
		if response.status_code == 200:
			return True,response.json()
		else:
			return False,response.json()
	except Exception as e:
		print(f"Error: {e} coming from get_slc_info ")
		return False,None


def get_list_camera_service() -> tuple:
	url = f"{current_app.config['BASE_URL']}/get-all-camera"
	try:
		response = requests.get(url,verify=False,timeout=10)
		if response.status_code == 200:
			return True,response.json()
		else:
			return False,response.json()
	except Exception as e:
		print(f"Error: {e} coming from get_list_camera_service")
		return False,None


def create_camera_service(data:dict) -> tuple:
	url =f"{current_app.config['BASE_URL']}/create_camera"
	try:
		response = requests.post(url,json=data,verify=False,timeout=10)
		if response.status_code == 200:
			return True,response.json()
		else:
			return False,response.json()
	except Exception as e:
		return False,None
