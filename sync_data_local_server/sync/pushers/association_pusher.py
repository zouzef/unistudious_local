import sys
import os
import logging
import requests
import json
from core.auth import get_token
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

BASE_SESSIONS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../../unistudious_local/attendance_system/dataset"
))

# ---------------------------------------------------------------------------
# Remote API calls
# ---------------------------------------------------------------------------

def _send_association(settings, image_path, user_id):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{settings.api_base_url}/slc/set-reference-student/{user_id}"

        # Build absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_image_path = os.path.abspath(os.path.join(
            base_dir,
            settings.uploads_path,
            image_path
        ))

        logger.debug(f"Image full path: {full_image_path}")

        if not os.path.exists(full_image_path):
            logger.warning(f"Image not found locally: {full_image_path}")
            return False

        with open(full_image_path, "rb") as img_file:
            files = {"file": (os.path.basename(full_image_path), img_file, "image/jpeg")}
            response = requests.post(url, headers=headers, files=files, verify=False, timeout=30)

        if response.status_code == 200:
            logger.info(f"✓ Image sent for user {user_id}: {os.path.basename(full_image_path)}")
            return True
        else:
            logger.warning(f"Failed to send image for user {user_id} — {response.status_code}: {response.text}")
            return False

    except Exception as e:
        logger.exception(f"Error in _send_association: {e}")
        return False



#  ---------------------------- Push association files to remote server ----------------------------
def push_AssociationAdd(db, settings, audit_row):
    """Push all images from sync_images row to remote server."""
    try:
        user_id     = audit_row.get("user_id")
        images_path = audit_row.get("images_path")
        audit_id    = audit_row.get("audit_id")

        if not user_id or not images_path:
            logger.warning("Missing user_id or images_path in audit_row")
            return False

        # images_path is stored as JSON list
        if isinstance(images_path, str):
            import json
            images_path = json.loads(images_path)

        if not images_path:
            logger.warning(f"Empty images_path for user {user_id}")
            return False

        logger.info(f"Pushing {len(images_path)} image(s) for user {user_id}...")

        success_count = 0
        for image_path in images_path:
            success = _send_association(settings, image_path, user_id)
            if success:
                success_count += 1

        if success_count == len(images_path):
            logger.info(f"✓ All {success_count} image(s) sent for user {user_id}")
            return True
        else:
            logger.warning(f"Only {success_count}/{len(images_path)} images sent for user {user_id}")
            return False

    except Exception as e:
        logger.exception("Error in push_AssociationAdd: %s", e)
        return False


def push_AssociationUpdate(db, settings, audit_row):
	pass


def push_AssociationDelete(db, settings, audit_row):
	pass


# ---------------------------------------------------------------------------
# Remote API calls
# ---------------------------------------------------------------------------
def _send_FolderNotAssociated(settings, folder_name, images_path, calander_prod_id):
    try:
        remote_base_url = settings.api_base_url
        token = settings.get_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # --- STEP 1: Send first image to create folder ---
        # Find first image that actually exists
        first_image = None
        first_image_full_path = None

        for img in images_path:
            candidate_path = os.path.join(BASE_SESSIONS_DIR, img)
            if os.path.exists(candidate_path):
                first_image = img
                first_image_full_path = candidate_path
                break

        if not first_image:
            logger.warning(f"No images found locally for folder {folder_name} — all deleted, marking as synced.")
            return True  # ← return True so it's marked synced and not retried forever

        with open(first_image_full_path, "rb") as f:
            response = requests.post(
                f"{remote_base_url}/slc/set-unknown-attendance-student-folder/{calander_prod_id}",
                headers=headers,
                files={"file": (os.path.basename(first_image), f)}
            )

        if response.status_code != 200:
            logger.warning(f"Failed to create folder on remote: {response.text}")
            return False

        folder_id = response.json().get("id")
        if not folder_id:
            logger.warning(f"No folder_id returned from remote")
            return False

        logger.info(f"✓ Remote folder created — folder_id={folder_id}")

        # --- STEP 2: Send remaining images using folder_id ---
        for image_path in images_path[1:]:
            full_path = os.path.join(BASE_SESSIONS_DIR, image_path)

            if not os.path.exists(full_path):
                logger.warning(f"Image not found locally, skipping: {os.path.basename(image_path)}")
                continue  # ← skip silently, don't fail

            with open(full_path, "rb") as f:
                res = requests.post(
                    f"{remote_base_url}/slc/set-unknown-attendance-student-file/{folder_id}",
                    headers=headers,
                    files={"file": (os.path.basename(image_path), f)}
                )

            if res.status_code == 200:
                logger.info(f"✓ Uploaded: {os.path.basename(image_path)}")
            else:
                logger.warning(f"Failed to upload {os.path.basename(image_path)}: {res.text}")

        return True

    except Exception as e:
        logger.exception(f"ERROR in _send_FolderNotAssociated: {e}")
        return False

# ---------------------------- push folder to remote server ----------------------------
def push_FolderNotAssociated(db, settings, audit_row):
    try:
        folder_name  = audit_row.get("folder_name")
        images_path  = json.loads(audit_row.get("images_path"))  # parse JSON string → list
        calendar_id  = audit_row.get("calendar_id")

        # --- GET calander_prod_id ---
        prod_query = """
            SELECT id_prod 
            FROM relation_calander_group_session 
            WHERE id = %s
        """
        result = db.fetch_query(prod_query, (calendar_id,))
        if not result:
            print(f"❌ No prod calendar found for calendar_id={calendar_id}")
            return False

        calander_prod_id = result[0].get("id_prod")

        # --- SEND TO REMOTE ---
        success = _send_FolderNotAssociated(settings, folder_name, images_path, calander_prod_id)

        return success

    except Exception as e:
        print(f"❌ ERROR in push_FolderNotAssociated: {str(e)}")
        return False
