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
