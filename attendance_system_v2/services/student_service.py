# service/student_service.py

from services.client import FlaskClient
from utils.logger import logger

def get_list_students(client: FlaskClient, calendar_id: int) -> list:
	"""Fech all students for a given calendar session."""
	try:
		response = client.get(f"/get-attendance/{calendar_id}")
		students = response.json().get("attendance",[])
		logger.info(f"Found {len(students)} student(s) for calendar {calendar_id}")
		return students
	except Exception as e:
		logger.error(f"Failed to fetch students for calendar {calendar_id}: {e}")
		return []

def store_classified_folders(client: FlaskClient, calendar_id: int) -> bool:
    """Store classified folders and image paths in DB after recognition."""
    try:
        response = client.post(f"/store-classified-folders/{calendar_id}")
        data = response.json()
        if data.get("success"):
            logger.info(f"Classified folders stored for calendar {calendar_id}: {data.get('stored')}")
            return True
        else:
            logger.warning(f"Failed to store classified folders for calendar {calendar_id}: {data}")
            return False
    except Exception as e:
        logger.error(f"Failed to store classified folders for calendar {calendar_id}: {e}")
        return False