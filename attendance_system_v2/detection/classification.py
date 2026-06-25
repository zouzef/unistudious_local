import os
import shutil
import requests
import json
from utils.logger import logger

with open("configurations.json") as f:
    _config = json.load(f)


COMPREFACE_API_KEY   = _config["compre_face"]["compreface_api_key"]
COMPREFACE_BASE_URL  = _config["compre_face"]["compreface_url"]
SIMILARITY_THRESHOLD = _config["compre_face"]["similarity_threshold"]
MAX_IMAGES_PER_PERSON = _config["compre_face"]["max_enroll_images"]

def verify_faces(source_path: str, target_path: str) -> bool:
    """
    Compare two face images using CompreFace verify endpoint.
    Returns True if similarity >= threshold.
    """
    endpoint = f"{COMPREFACE_BASE_URL}/api/v1/verification/verify"
    headers  = {"x-api-key": COMPREFACE_API_KEY}

    try:
        with open(source_path, "rb") as src, open(target_path, "rb") as tgt:
            files = {
                "source_image": src,
                "target_image": tgt,
            }
            response = requests.post(endpoint, files=files, headers=headers, timeout=10)
            print("RAW RESPONSE:", response.status_code, response.text)
            result   = response.json()

        result_list = result.get("result", [])
        if not result_list or "face_matches" not in result_list[0]:
            logger.debug(f"No face match found: {os.path.basename(source_path)} ↔ {os.path.basename(target_path)}")
            return False

        face_matches = result_list[0]["face_matches"]
        if not face_matches:
            logger.debug(f"No similar match: {os.path.basename(source_path)} ↔ {os.path.basename(target_path)}")
            return False

        similarity = face_matches[0].get("similarity", 0)
        logger.debug(f"{os.path.basename(source_path)} ↔ {os.path.basename(target_path)} → similarity: {similarity:.4f}")
        return similarity >= SIMILARITY_THRESHOLD

    except Exception as e:
        logger.error(f"CompreFace verify error: {e}")
        return False


def classify_faces(calendar_id: int, max_images_per_person: int = MAX_IMAGES_PER_PERSON) -> str | None:
    """
    Classify face crops from a session into person folders using CompreFace.

    Input  : dataset/session_{calendar_id}/face_crops/
    Output : dataset/session_{calendar_id}/classified/person_1/, person_2/, ...

    Returns the classified output directory path, or None on failure.
    """
    input_dir  = os.path.join("dataset", f"session_{calendar_id}", "face_crops")
    output_dir = os.path.join("dataset", f"session_{calendar_id}", "classified")

    if not os.path.exists(input_dir):
        logger.error(f"face_crops folder not found: {input_dir}")
        return None

    images = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not images:
        logger.warning(f"No images found in {input_dir}")
        return None

    logger.info(f"Starting classification for calendar {calendar_id} — {len(images)} image(s) found.")
    os.makedirs(output_dir, exist_ok=True)

    unprocessed = images.copy()
    group_id    = 1

    while unprocessed:
        ref_img  = unprocessed.pop(0)
        ref_path = os.path.join(input_dir, ref_img)

        person_folder = os.path.join(output_dir, f"person_{group_id}")
        os.makedirs(person_folder, exist_ok=True)
        shutil.copy(ref_path, os.path.join(person_folder, ref_img))
        logger.info(f"Created person_{group_id} — reference: {ref_img}")

        group_images  = [ref_path]
        copied_count  = 1          # reference image already copied

        matched = []
        for img in unprocessed:
            img_path = os.path.join(input_dir, img)

            is_match = any(verify_faces(group_img, img_path) for group_img in group_images)

            if is_match:
                matched.append(img)
                group_images.append(img_path)  # always track for future comparisons

                # Only copy if we haven't reached the limit yet
                if copied_count < max_images_per_person:
                    shutil.copy(img_path, os.path.join(person_folder, img))
                    copied_count += 1
                    logger.info(f"  ✔ Copied {img} → person_{group_id} ({copied_count}/{max_images_per_person})")
                else:
                    logger.info(f"  ⏭ Matched {img} → person_{group_id} (limit reached, skipped copy)")

        for m in matched:
            unprocessed.remove(m)

        group_id += 1

    logger.info(f"Classification complete — {group_id - 1} person(s) found for calendar {calendar_id}.")
    return output_dir