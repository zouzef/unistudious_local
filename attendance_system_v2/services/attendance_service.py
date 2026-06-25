from services.client import FlaskClient
from utils.logger import logger

def update_attendance(client: FlaskClient, attendance_id: int, is_present: bool) -> bool:
	"""Update attendance status for a student."""
	try:
		print(is_present)

		response = client.post(
			f"/update-attendance-student/{attendance_id}",
			json = {"status": is_present}
		)
		logger.info(f"Attendance {attendance_id} updated - present: {is_present}.")
		return True
	except Exception as e:
		logger.error(f"Failed to update {attendance_id}: {e}")
		return False

def get_present_students(client: FlaskClient, calendar_id: int) -> set:
    """
    Get set of userIds already marked present for a calendar.
    Used to avoid overwriting real-time recognition results.
    """
    try:
        from services.student_service import get_list_students
        students = get_list_students(client, calendar_id)
        return set(
            str(s.get("userId"))
            for s in students
            if s.get("isPresent") is True
        )
    except Exception as e:
        logger.error(f"Failed to get present students for calendar {calendar_id}: {e}")
        return set()