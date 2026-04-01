# main.py

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
MAC      = config["slc_config"]["MAC"]
PASSWORD = config["slc_config"]["PASSWORD"]


def main():
    logger.info("Server is starting...")

    # --- STEP 1: LOGIN ---
    token = login_slc(BASE_URL, MAC, PASSWORD)
    if not token:
        logger.error("Login failed. Exiting.")
        return

    # --- STEP 2: CREATE CLIENT ---
    client = FlaskClient(BASE_URL, token=token)

    # --- TRACKING LISTS ---
    started_calendars   = []   # calendars we already started
    active_calendars    = []   # calendars currently running
    completed_calendars = []   # calendars fully finished
    rooms_without_cameras = set()

    while True:
        try:
            now = datetime.now()
            logger.info(f"Checking calendars at {now.strftime('%H:%M:%S')}")

            # --- STEP 3: GET CALENDARS ---
            calendars = get_all_calendars(client)

            if not calendars:
                logger.info("No calendars found for today.")
            else:
                calendars_soon = []

                for calendar in calendars:
                    # Skip already completed
                    if calendar["id"] in completed_calendars:
                        continue

                    # Skip already ended
                    if now > calendar["endTime"]:
                        logger.info(f"Calendar {calendar['id']} already ended — skipping.")
                        continue

                    # Skip rooms with no cameras
                    if calendar["roomId"] in rooms_without_cameras:
                        logger.info(f"Room {calendar['roomId']} has no cameras — skipping.")
                        continue

                    time_to_start = (calendar["startTime"] - now).total_seconds()

                    # Only process calendars starting within 15 minutes or already started
                    if time_to_start <= 900:
                        calendars_soon.append(calendar)
                    else:
                        logger.info(
                            f"Calendar {calendar['id']} starts in "
                            f"{int(time_to_start // 60)} min — waiting."
                        )

                # --- STEP 4: PROCESS CALENDARS STARTING SOON ---
                for calendar in calendars_soon:
                    if calendar["id"] in started_calendars:
                        logger.info(f"Calendar {calendar['id']} already started — skipping.")
                        continue

                    logger.info(f"Processing calendar {calendar['id']} in room {calendar['roomId']}...")

                    # --- GET CAMERAS ---
                    cameras = get_all_camera(client, calendar["roomId"])
                    if not cameras:
                        logger.warning(f"No cameras in room {calendar['roomId']} — skipping.")
                        rooms_without_cameras.add(calendar["roomId"])
                        continue

                    for cam in cameras:
                        logger.info(f"  Camera: {cam['name']} — mac: {cam['mac']} — status: {cam['status']}")

                    # --- GET STUDENTS ---
                    attendances = get_list_students(client, calendar["id"])
                    if not attendances:
                        logger.warning(f"No students found for calendar {calendar['id']} — skipping.")
                        continue

                    for attendance in attendances:
                        logger.info(f"  Student: {attendance['userName']} — present: {attendance['isPresent']}")

                    # --- MARK AS STARTED ---
                    started_calendars.append(calendar["id"])
                    active_calendars.append({
                        "calendar_id": calendar["id"],
                        "room_id":     calendar["roomId"],
                        "end_time":    calendar["endTime"],
                        "cameras":     cameras,
                        "attendances": attendances,
                    })
                    logger.info(f"Calendar {calendar['id']} started successfully.")

            # --- STEP 5: CHECK FINISHED CALENDARS ---
            finished = []
            for active in active_calendars:
                if now >= active["end_time"]:
                    logger.info(f"Calendar {active['calendar_id']} has ended — cleaning up...")
                    # TODO: stop detection processes here later
                    finished.append(active["calendar_id"])
                    logger.info(f"Calendar {active['calendar_id']} completed.")
                else:
                    remaining = (active["end_time"] - now).total_seconds()
                    logger.info(
                        f"Calendar {active['calendar_id']} still running "
                        f"({int(remaining // 60)}m {int(remaining % 60)}s remaining)."
                    )

            # --- STEP 6: MOVE FINISHED TO COMPLETED ---
            for calendar_id in finished:
                started_calendars = [s for s in started_calendars if s != calendar_id]
                active_calendars  = [a for a in active_calendars if a["calendar_id"] != calendar_id]
                completed_calendars.append(calendar_id)

            if active_calendars:
                logger.info(f"Active calendars: {[a['calendar_id'] for a in active_calendars]}")

            time.sleep(10)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(10)
            continue


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("spawn")
    main()