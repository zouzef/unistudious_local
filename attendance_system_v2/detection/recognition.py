# detection/recognition.py

import os
import json
import requests
import shutil
from utils.logger import logger

# --- Load config ---
with open("configurations.json") as f:
    _config = json.load(f)

RECOGNITION_API_KEY   = _config["compre_face"]["recognition_api_key"]
COMPREFACE_BASE_URL   = _config["compre_face"]["compreface_url"]
USER_IMGS_PATH        = _config["user_imgs_path"]
MAX_ENROLL_IMAGES     = _config["compre_face"]["max_enroll_images"]
RECOGNITION_THRESHOLD = _config["compre_face"]["recognition_threshold"]

ENROLL_ENDPOINT    = f"{COMPREFACE_BASE_URL}/api/v1/recognition/faces"
SUBJECTS_ENDPOINT  = f"{COMPREFACE_BASE_URL}/api/v1/recognition/subjects"
RECOGNIZE_ENDPOINT = f"{COMPREFACE_BASE_URL}/api/v1/recognition/recognize"
HEADERS            = {"x-api-key": RECOGNITION_API_KEY}
DETECTION_THRESHOLD   = _config["compre_face"].get("det_prob_threshold", 0.8)

def get_enrolled_subjects() -> set:
    try:
        response = requests.get(SUBJECTS_ENDPOINT, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return set(str(s) for s in data.get("subjects", []))
        else:
            logger.warning(f"Failed to fetch enrolled subjects — {response.status_code}: {response.text}")
            return set()
    except Exception as e:
        logger.error(f"Error fetching enrolled subjects: {e}")
        return set()


def enroll_students(students: list) -> int:
    enrolled         = 0
    already_enrolled = get_enrolled_subjects()
    logger.info(f"Found {len(already_enrolled)} subject(s) already enrolled in CompreFace.")

    for student in students:
        user_id      = student.get("userId")
        user_ref_rlc = student.get("userRefRlc")

        if not user_id:
            logger.warning("Student has no userId — skipping.")
            continue

        if not user_ref_rlc:
            logger.warning(f"Student {user_id} has no reference photo (userRefRlc is null) — skipping.")
            continue

        if str(user_id) in already_enrolled:
            logger.info(f"Student {user_id} already enrolled in CompreFace — skipping.")
            continue

        ref_img_dir = os.path.join(USER_IMGS_PATH, f"user_{user_id}", "ref_img")

        if not os.path.exists(ref_img_dir):
            logger.warning(f"Student {user_id} — ref_img folder not found: {ref_img_dir}")
            continue

        images = [
            f for f in os.listdir(ref_img_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ][:MAX_ENROLL_IMAGES]

        if not images:
            logger.warning(f"Student {user_id} — no image found in {ref_img_dir}")
            continue

        for img_name in images:
            ref_image_path = os.path.join(ref_img_dir, img_name)
            try:
                with open(ref_image_path, "rb") as img_file:
                    response = requests.post(
                        ENROLL_ENDPOINT,
                        headers=HEADERS,
                        files={"file": img_file},
                        params={
                            "subject": str(user_id),
                            "det_prob_threshold": DETECTION_THRESHOLD
                        },
                        timeout=10
                    )
                if response.status_code in (200, 201):
                    logger.info(f"Enrolled image {img_name} for student {user_id}.")
                else:
                    logger.warning(f"Failed to enroll {img_name} for student {user_id} — {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Error enrolling {img_name} for student {user_id}: {e}")

        enrolled += 1

    logger.info(f"Enrollment complete — {enrolled}/{len(students)} student(s) enrolled.")
    return enrolled


def unenroll_students(students: list) -> None:
    for student in students:
        user_id = student.get("userId")
        if not user_id:
            continue
        try:
            response = requests.delete(
                f"{COMPREFACE_BASE_URL}/api/v1/recognition/faces",
                headers=HEADERS,
                params={"subject": str(user_id)},
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Unenrolled student {user_id} from CompreFace.")
            else:
                logger.warning(f"Failed to unenroll student {user_id} — {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error unenrolling student {user_id}: {e}")


def recognize_persons(calendar_id: int) -> dict:
    classified_dir = os.path.join("dataset", f"session_{calendar_id}", "classified")

    if not os.path.exists(classified_dir):
        logger.error(f"Classified folder not found: {classified_dir}")
        return {}

    results            = {}
    seen_users         = set()
    recognized_folders = []

    person_folders = sorted([
        f for f in os.listdir(classified_dir)
        if os.path.isdir(os.path.join(classified_dir, f))
    ])

    if not person_folders:
        logger.warning(f"No person folders found in {classified_dir}")
        return {}

    logger.info(f"Recognizing {len(person_folders)} person(s) for calendar {calendar_id}...")

    for person in person_folders:
        person_path = os.path.join(classified_dir, person)

        images = [
            f for f in os.listdir(person_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not images:
            logger.warning(f"{person} — no images found, skipping.")
            continue

        votes = {}

        for img_name in images:
            img_path = os.path.join(person_path, img_name)

            try:
                with open(img_path, "rb") as img_file:
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
                    logger.warning(f"{person}/{img_name} — CompreFace error {response.status_code}: {response.text}")
                    continue

                data        = response.json()
                result_list = data.get("result", [])

                if not result_list or "subjects" not in result_list[0]:
                    logger.warning(f"{person}/{img_name} — no subjects returned.")
                    continue

                subjects = result_list[0]["subjects"]
                if not subjects:
                    logger.warning(f"{person}/{img_name} — no match found.")
                    continue

                best_match = subjects[0]
                user_id    = best_match.get("subject")
                similarity = best_match.get("similarity", 0)

                if user_id not in votes:
                    votes[user_id] = []
                votes[user_id].append(similarity)

                logger.debug(f"{person}/{img_name} → userId={user_id} (similarity={similarity:.4f})")

            except Exception as e:
                logger.error(f"Error recognizing {person}/{img_name}: {e}")
                continue

        if not votes:
            logger.warning(f"{person} — no votes collected, skipping.")
            continue

        best_user_id   = max(votes, key=lambda uid: (len(votes[uid]), sum(votes[uid]) / len(votes[uid])))
        avg_similarity = sum(votes[best_user_id]) / len(votes[best_user_id])
        vote_count     = len(votes[best_user_id])

        if avg_similarity < RECOGNITION_THRESHOLD:
            logger.warning(f"{person} → rejected (avg similarity={avg_similarity:.4f} < threshold={RECOGNITION_THRESHOLD})")
            continue

        if best_user_id in seen_users:
            logger.warning(f"{person} → userId={best_user_id} already assigned — skipping.")
            continue

        seen_users.add(best_user_id)
        recognized_folders.append(person_path)
        logger.info(f"{person} → userId={best_user_id} ({vote_count} votes, avg similarity={avg_similarity:.4f})")
        results[best_user_id] = avg_similarity

    # ✅ Delete recognized folders, keep unknown ones
    for folder_path in recognized_folders:
        try:
            shutil.rmtree(folder_path)
            logger.info(f"Deleted recognized folder: {os.path.basename(folder_path)}")
        except Exception as e:
            logger.error(f"Error deleting folder {folder_path}: {e}")

    remaining = len(person_folders) - len(recognized_folders)
    logger.info(f"Cleanup complete — {len(recognized_folders)} folder(s) deleted, {remaining} unknown folder(s) kept.")
    logger.info(f"Recognition complete — {len(results)} student(s) identified.")
    return results