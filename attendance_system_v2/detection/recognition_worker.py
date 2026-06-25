# detection/recognition_worker.py

import os
import json
import requests
from utils.logger import logger

with open("configurations.json") as f:
    _config = json.load(f)

RECOGNITION_API_KEY   = _config["compre_face"]["recognition_api_key"]
COMPREFACE_BASE_URL   = _config["compre_face"]["compreface_url"]
RECOGNITION_THRESHOLD = _config["compre_face"]["recognition_threshold"]
DETECTION_THRESHOLD   = _config["compre_face"].get("det_prob_threshold", 0.8)

RECOGNIZE_ENDPOINT = f"{COMPREFACE_BASE_URL}/api/v1/recognition/recognize"
HEADERS            = {"x-api-key": RECOGNITION_API_KEY}


def recognition_worker(recognition_queue, stop_event, attendances, calendar_id, client):
    """
    Worker process that reads face crops from queue,
    sends to CompreFace, and updates attendance in real-time.
    Stops when all students are recognized or session ends.
    """
    from services.attendance_service import update_attendance

    # Build attendance map userId → attendance id
    attendance_map = {
        str(student.get("userId")): student.get("id")
        for student in attendances
    }

    # Track recognized students
    recognized_cache = set()
    total_students   = len([s for s in attendances if s.get("userRefRlc")])

    logger.info(f"Recognition worker started for calendar {calendar_id} — {total_students} student(s) to recognize.")

    while not stop_event.is_set():

        # ✅ Stop early if all students recognized
        if len(recognized_cache) >= total_students:
            logger.info(f"All {total_students} students recognized — worker stopping early.")
            break

        try:
            # Wait for a face crop from the queue (timeout so we can check stop_event)
            try:
                item = recognition_queue.get(timeout=2)
            except Exception:
                continue  # timeout — check stop_event and try again

            face_path = item.get("face_path")

            if not face_path or not os.path.exists(face_path):
                logger.debug(f"Face path not found: {face_path} — skipping.")
                continue

            # Send to CompreFace
            with open(face_path, "rb") as img_file:
                response = requests.post(
                    RECOGNIZE_ENDPOINT,
                    headers=HEADERS,
                    files={"file": img_file},
                    params={
                        "limit": 1,
                        "det_prob_threshold": DETECTION_THRESHOLD
                    },
                    timeout=10
                )

            if response.status_code != 200:
                logger.debug(f"CompreFace error {response.status_code} — skipping.")
                continue

            data        = response.json()
            result_list = data.get("result", [])

            if not result_list or "subjects" not in result_list[0]:
                continue

            subjects = result_list[0]["subjects"]
            if not subjects:
                continue

            best_match = subjects[0]
            user_id    = best_match.get("subject")
            similarity = best_match.get("similarity", 0)

            if similarity < RECOGNITION_THRESHOLD:
                logger.debug(f"Low similarity {similarity:.4f} — skipping.")
                continue

            if user_id in recognized_cache:
                logger.debug(f"Student {user_id} already recognized — skipping.")
                # ✅ Delete the duplicate face crop
                try:
                    os.remove(face_path)
                except:
                    pass
                continue

            # ✅ New student recognized!
            recognized_cache.add(user_id)
            attendance_id = attendance_map.get(str(user_id))

            if attendance_id:
                update_attendance(client, attendance_id, True)
                logger.info(f"✅ Student {user_id} recognized (similarity={similarity:.4f}) — attendance updated.")
            else:
                logger.warning(f"No attendance id found for userId={user_id}")

            # ✅ Unenroll from CompreFace — no need to recognize again
            try:
                requests.delete(
                    f"{COMPREFACE_BASE_URL}/api/v1/recognition/faces",
                    headers=HEADERS,
                    params={"subject": str(user_id)},
                    timeout=10
                )
                logger.info(f"Unenrolled student {user_id} from CompreFace.")
            except Exception as e:
                logger.error(f"Error unenrolling student {user_id}: {e}")

            # ✅ Delete the face crop — student is known
            try:
                os.remove(face_path)
            except:
                pass

        except Exception as e:
            logger.error(f"Recognition worker error: {e}")
            continue

    logger.info(f"Recognition worker finished for calendar {calendar_id} — {len(recognized_cache)} student(s) recognized.")
    return recognized_cache