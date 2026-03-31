# services/attendance_service.py

from services.client import FlaskClient
from utils.logger import logger


def send_recording_data(client: FlaskClient, session_id: str, folder_path: str, config: dict):
    """Send recorded attendance data back to Flask server."""
    try:
        path = config["endpoints"]["recordings"]
        response = client.post(path, json={
            "session_id": session_id,
            "folder_path": folder_path
        })
        logger.info(f"Recording data sent for session {session_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send recording data for session {session_id}: {e}")


def run_post_treatment(client: FlaskClient, session_id: str, config: dict):
    """Trigger post-treatment processing for a finished session."""
    try:
        path = config["endpoints"]["post_treatment"].format(session_id=session_id)
        response = client.post(path)
        logger.info(f"Post-treatment done for session {session_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Post-treatment failed for session {session_id}: {e}")