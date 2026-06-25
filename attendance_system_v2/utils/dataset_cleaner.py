# utils/dataset_cleaner.py

import os
import shutil
from utils.logger import logger


def cleanup_session_dataset(calendar_id: int) -> None:
    """
    After session ends:
    - Delete face_crops folder (raw crops no longer needed)
    - Keep classified folder (unknown persons for teacher review)
    """
    face_crops_dir = os.path.join("dataset", f"session_{calendar_id}", "face_crops")

    if os.path.exists(face_crops_dir):
        try:
            shutil.rmtree(face_crops_dir)
            logger.info(f"Deleted face_crops for session {calendar_id}.")
        except Exception as e:
            logger.error(f"Error deleting face_crops for session {calendar_id}: {e}")
    else:
        logger.warning(f"face_crops folder not found for session {calendar_id} — skipping.")