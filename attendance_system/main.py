# main.py

import json
import time
from datetime import datetime,timedelta

from services.auth_service import login_slc
from services.client import FlaskClient
from services.calendar_service import get_all_calendars
from services.student_service import get_list_students, store_classified_folders
from services.camera_service import get_all_camera
from services.attendance_service import update_attendance

from detection.detector import start_detection_for_calendar, stop_detection_for_calendar
from detection.classification import classify_faces
from detection.recognition import enroll_students, unenroll_students, recognize_persons

from utils.logger import logger
from utils.dataset_cleaner import cleanup_session_dataset


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
    started_calendars     = []
    active_calendars      = []
    completed_calendars   = []
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
                    if calendar["id"] in completed_calendars:
                        continue
                    if now > calendar["endTime"]:
                        logger.info(f"Calendar {calendar['id']} already ended — skipping.")
                        continue
                    if calendar["roomId"] in rooms_without_cameras:
                        logger.info(f"Room {calendar['roomId']} has no cameras — skipping.")
                        continue

                    time_to_start = (calendar["startTime"] - now).total_seconds()
                    if time_to_start <= 900:
                        calendars_soon.append(calendar)
                    else:
                        logger.info(
                            f"Calendar {calendar['id']} starts in "
                            f"{int(time_to_start // 60)} min — waiting."
                        )

                # --- STEP 4: START DETECTION FOR CALENDARS STARTING SOON ---
                for calendar in calendars_soon:
                    if calendar["id"] in started_calendars:
                        logger.info(f"Calendar {calendar['id']} already started — skipping.")
                        continue

                    logger.info(f"Processing calendar {calendar['id']} in room {calendar['roomId']}...")

                    cameras = get_all_camera(client, calendar["roomId"])
                    if not cameras:
                        logger.warning(f"No cameras in room {calendar['roomId']} — skipping.")
                        rooms_without_cameras.add(calendar["roomId"])
                        continue

                    attendances = get_list_students(client, calendar["id"])
                    if not attendances:
                        logger.warning(f"No students for calendar {calendar['id']} — skipping.")
                        continue

                    logger.info(f"Enrolling students for calendar {calendar['id']}...")
                    enroll_students(attendances)

                    # ✅ START CAMERA DETECTION
                    processes, stop_event = start_detection_for_calendar(
                        calendar_id=calendar["id"],
                        room_id=calendar["roomId"],
                        cameras=cameras
                    )

                    if not processes:
                        logger.warning(f"No detection processes started for calendar {calendar['id']} — skipping.")
                        continue

                    started_calendars.append(calendar["id"])
                    active_calendars.append({
                        "calendar_id": calendar["id"],
                        "room_id":     calendar["roomId"],
                        "end_time":    calendar["startTime"] + timedelta(minutes=2),
                        "cameras":     cameras,
                        "attendances": attendances,
                        "processes":   processes,    # ✅ store processes
                        "stop_event":  stop_event,   # ✅ store stop_event
                    })
                    logger.info(f"Calendar {calendar['id']} started — {len(processes)} camera(s) running.")

            # --- STEP 5: STOP DETECTION FOR FINISHED CALENDARS ---
            finished = []
            for active in active_calendars:
                if now >= active["end_time"]:
                    logger.info(f"Calendar {active['calendar_id']} ended — stopping cameras...")

                    # ✅ STOP CAMERA DETECTION
                    stop_detection_for_calendar(
                        calendar_id=active["calendar_id"],
                        processes=active["processes"],
                        stop_event=active["stop_event"]
                    )

                    # ✅ CLASSIFY FACES
                    classify_faces(active["calendar_id"])

                    # ✅ RECOGNIZE PERSONS
                    logger.info(f"Recognizing persons for calendar {active['calendar_id']}...")
                    recognized = recognize_persons(active["calendar_id"])
                    logger.info(f"Recognized students: {recognized}")

                    # ✅ STORE CLASSIFIED FOLDERS + IMAGE PATHS IN DB
                    store_classified_folders(client, active["calendar_id"])

                    # ✅ BUILD userId → attendance id map
                    attendance_map = {
                        str(student.get("userId")): student.get("id")
                        for student in active["attendances"]
                    }

                    # ✅ UPDATE ATTENDANCE
                    for student in active["attendances"]:
                        user_id = str(student.get("userId"))
                        attendance_id = attendance_map.get(user_id)
                        is_present = user_id in recognized  # recognized = {"3": 0.92}

                        if attendance_id is None:
                            logger.warning(f"No attendance id found for userId={user_id} — skipping.")
                            continue

                        update_attendance(client, attendance_id, is_present)

                    # ✅ UNENROLL STUDENTS FROM COMPREFACE
                    logger.info(f"Unenrolling students for calendar {active['calendar_id']}...")
                    unenroll_students(active["attendances"])

                    # ✅ CLEANUP face_crops, keep unknown classified folders
                    cleanup_session_dataset(active["calendar_id"])

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
                active_calendars  = [a for a in active_calendars  if a["calendar_id"] != calendar_id]
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