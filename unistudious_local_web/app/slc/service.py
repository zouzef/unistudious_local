import requests
import os
import base64
from flask import current_app


def get_slc_info_service(account_id: int) -> tuple:
	""" GET slc_info"""
	url = f"{current_app.config['BASE_URL']}get_local_detail/{account_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json(), 200
		else:
			return False, response.json(), response.status_code
	except requests.exceptions.ConnectionError:
		return False, {"Message": "Local server unreachable"}, 503
	except requests.exceptions.Timeout:
		return False, {"Message": "Local server timed out"}, 504
	except Exception as e:
		print(f"Error: {e} coming from get_slc_info")
		return False, {"Message": str(e)}, 500


# ====================================================== CAMERA services ======================================================
def get_list_camera_service() -> tuple:
	url = f"{current_app.config['BASE_URL']}get-all-camera"
	try:
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()
	except Exception as e:
		print(f"Error: {e} coming from get_list_camera_service")
		return False, None


def create_camera_service(data: dict) -> tuple:
	url = f"{current_app.config['BASE_URL']}create_camera"
	try:
		response = requests.post(url, json=data, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()
	except Exception as e:
		return False, None


def update_camera_service(data: dict, camera_id: int) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}update_camera/{camera_id}"
		response = requests.post(url, json=data, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()
	except Exception as e:
		print(e)
		return False, None


def delete_camera_service(tablet_id: int) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}delete_camera/{tablet_id}"
		response = requests.post(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		})


# ====================================================== TABLET service ======================================================


def create_tablet_service(data: dict) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}create_tablet"
		response = requests.post(url, json=data, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()

	except Exception as e:
		print(e)
		return False, None


def update_tablet_service(data: dict, id_tablet: int) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}update_tablet/{id_tablet}"
		response = requests.post(url, json=data, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()
	except Exception as e:
		print(e)
		return False, None


def delete_tablet_service(tablet_id: int) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}delete_tablet/{tablet_id}"
		response = requests.post(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()

	except Exception as e:
		print(e)
		return False, None


def fetch_all_tablet_service() -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}get-all-tablets"
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()


	except Exception as e:
		print(e)
		return False, None


def view_tablet_service(tablet_id: int) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}view-tablet/{tablet_id}"
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()

	except Exception as e:
		print(e)
		return False, None


# ====================================================== ROOM service ======================================================
def fetch_room_service() -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}get-all-room"
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()

	except Exception as e:

		return False, None


def create_room_service(room_data) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}create_room"
		response = requests.post(url, json=room_data, verify=False, timeout=10)
		try:
			body = response.json()
		except ValueError:
			body = {"Message": "Invalid response from main server"}
		return response.status_code == 200, body
	except Exception as e:
		print(f"Error: {e} coming from create_room_service")
		return False, None


def delete_room_service(room_id: int) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}delete_room/{room_id}"
		response = requests.post(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response.json()
		else:
			return False, response.json()
	except Exception as e:
		return False, None


def update_room_service(id_room: int, data: dict) -> tuple:
	try:
		url = f"{current_app.config['BASE_URL']}update_room/{id_room}"
		response = requests.post(url, json=data, verify=False, timeout=10)

		try:
			body = response.json()
		except ValueError:
			body = {"Message": f"Unexpected response from main server ({response.status_code})"}

		return response.status_code == 200, body

	except requests.exceptions.Timeout:
		return False, {"Message": "Main server timed out"}
	except requests.exceptions.RequestException as e:
		return False, {"Message": f"Could not reach main server: {e}"}

# ====================================================== LOCAL service ======================================================
def get_local_info_service(account_id):
	url = f"{current_app.config['BASE_URL']}get_local_detail/{account_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			return True, response
		else:
			return False, response
	except Exception as e:
		return False, None
