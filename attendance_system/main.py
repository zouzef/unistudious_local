# Main.py

import json
import time
from datetime import datetime
from services.auth_service import login_slc
from services.client import FlaskClient
from services.calendar_service import get_all_calendars
from services.student_service import get_list_students
from services.camera_service import get_all_camera
from utils.logger import logger



PATH_CONFIG = "configurations.json"
with open(PATH_CONFIG) as f:
	config = json.load(f)

BASE_URL = config["slc_config"]["BASE_URL"]
MAC = config["slc_config"]["MAC"]
PASSWORD = config["slc_config"]["PASSWORD"]

def main():
	logger.info("Server is starting")

	# --- STEP 1: LOGIN ---
	token = login_slc(BASE_URL,MAC,PASSWORD)
	if not token:
			logger.error("Login failed , Existing.")
			return

	# --- STEP 2: CREATE CLIENT ---
	client = FlaskClient(BASE_URL,token=token)
	while True:
		try:
			now = datetime.now()
			logger.info(f"Checking sessions at {now.strftime('%H:%M:%S')}")

			# --- STEP 3: GET CALENDAR ---
			calendars = get_all_calendars(client)
			if not calendars:
				logger.info("No session found for today.")
			else:

				for calander in calendars:
					# ⛔ Skip expired sessions
					if now > calander['endTime']:
						logger.info(f"Skipping session {calander['id']} (already ended)")
						continue

					logger.info(
						f"Session {calander['id']} — room {calander['roomId']} — starts {calander['startTime'].strftime('%H:%M:%S')} — ends {calander['endTime'].strftime('%H:%M:%S')}"
					)

					# --- STEP 4: GET CAMERAS ---
					cameras = get_all_camera(client, calander["roomId"])
					if not cameras:
						logger.info(f"No cameras found for room {calander['roomId']} - skipping.")
						continue

					for cam in cameras:
						logger.info(f"  Camera: {cam['name']} — mac: {cam['mac']} — status: {cam['status']}")

					# --- STEP 5: GET STUDENTS ---
					attendances = get_list_students(client, calander["id"])
					print("Today attendance: ",attendances)


					if not attendances:
						logger.warning(f"No attendances found for session {calander['id']}")
						continue

					for attendance in attendances:
						logger.info(f" Student: {attendance['id']} - Present {attendance['isPresent']}")

			time.sleep(10)
		except Exception as e:
			logger.error(f"Error in main loop: {e}")
			time.sleep(10)
			continue

if __name__ == "__main__":
	import multiprocessing
	multiprocessing.set_start_method("spawn")
	main()


