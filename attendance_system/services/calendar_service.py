# services/calendar_service.py

from services.client import FlaskClient
from utils.logger import logger


def get_all_calendars(client: FlaskClient, config: dict) -> dict:
    """Fetch all calendar sessions from Flask server."""
    try:
        path = config["endpoints"]["calendars"]
        response = client.get(path)
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch calendars: {e}")
        return {"data": []}