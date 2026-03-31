# services/room_service.py

from services.client import FlaskClient
from utils.logger import logger


def get_all_camera(client: FlaskClient, room_id: str, config: dict) -> list:
    """Fetch all cameras for a given room."""
    try:
        path = config["endpoints"]["cameras"].format(room_id=room_id)
        response = client.get(path)
        return response.json().get("data", [])
    except Exception as e:
        logger.error(f"Failed to fetch cameras for room {room_id}: {e}")
        return []