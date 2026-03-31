# services/camera_service.py

from services.client import FlaskClient
from utils.logger import logger


def get_camera_stream_url(client: FlaskClient, camera_id: str, config: dict) -> str | None:
    """Fetch the stream URL for a specific camera."""
    try:
        path = config["endpoints"]["camera_stream"].format(camera_id=camera_id)
        response = client.get(path)
        return response.json().get("stream_url")
    except Exception as e:
        logger.error(f"Failed to fetch stream URL for camera {camera_id}: {e}")
        return None