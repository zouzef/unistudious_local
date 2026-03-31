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
