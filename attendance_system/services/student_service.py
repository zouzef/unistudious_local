# services/student_service.py

from services.client import FlaskClient
from utils.logger import logger


def get_list_students(client: FlaskClient, session: dict, config: dict) -> list:
    """Fetch all students enrolled in a session."""
    try:
        path = config["endpoints"]["students"].format(
            session_id=session["id"]
        )
        response = client.get(path)
        return response.json().get("data", [])
    except Exception as e:
        logger.error(f"Failed to fetch students for session {session['id']}: {e}")
        return []