# Services/room_service.py

from services.client import FlaskClient
from utils.logger import logger

def get_all_camera(client: FlaskClient, room_id: int) -> list:
	"""Fetch all cameras for a gven room."""
	try:
		response = client.get(f"/get-all-camera-room/{room_id}")
		cameras = response.json()
		logger.info(f"Fond {len(cameras)} camera(s) in room{room_id}.")
		return cameras

	except Exception as e:
		logger.info(f"Failed to fetch cameras for room {room_id}: {e}")
		return []