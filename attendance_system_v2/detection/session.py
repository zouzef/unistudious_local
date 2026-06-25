# detection/session.py

import os
from utils.logger import logger


def create_dataset_folders(calendar_id: int) -> tuple:
    """
    Create dataset folder structure for a specific calendar session.
    Creates:
      dataset/session_{calendar_id}/
      dataset/session_{calendar_id}/face_crops/
      dataset/session_{calendar_id}/all_frames/
      dataset/session_{calendar_id}/pkl_files/
    """
    main_dir      = os.path.join("dataset", f"session_{calendar_id}")
    face_crops_dir = os.path.join(main_dir, "face_crops")
    full_frames_dir = os.path.join(main_dir, "all_frames")
    pkl_dir       = os.path.join(main_dir, "pkl_files")

    try:
        os.makedirs(face_crops_dir, exist_ok=True)
        os.chmod(face_crops_dir, 0o777)
        os.makedirs(full_frames_dir, exist_ok=True)
        os.chmod(full_frames_dir, 0o777)
        os.makedirs(pkl_dir, exist_ok=True)
        os.chmod(pkl_dir, 0o777)
        os.chmod(main_dir, 0o777)
        logger.info(f"Created dataset folders for calendar {calendar_id}.")
        return face_crops_dir, full_frames_dir, pkl_dir

    except Exception as e:
        logger.error(f"Failed to create folders for calendar {calendar_id}: {e}")
        return None, None, None