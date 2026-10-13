# app/ecran/service.py
import requests
from flask import current_app


def get_ecran_events() -> list:
	"""
	Get ALL calendar events (every session) for the public screen.

	Calls a read-only endpoint on server_local_api. Each item must contain ONLY:
		id, title, color, start_time, end_time, room_name, teacher_name
	"""
	url = f"{current_app.config['BASE_URL']}get_ecran_events"
	try:
		response = requests.get(url, verify=False, timeout=10)
		response.raise_for_status()
		return response.json().get('data', [])
	except Exception as e:
		print(f"[ECRAN ERROR] get_ecran_events: {e}")
		return []