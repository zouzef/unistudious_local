# detection/camera.py

import os
import cv2
import time
import torch
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from insightface.app import FaceAnalysis    # ← ADD THIS
from utils.logger import logger
from detection.session import create_dataset_folders

MODEL_PATH = "best.pt"
PADDING_PERCENT = 0.20
QUALITY_THRESHOLD = 0.20


# --- InsightFace quality checker (initialized once) ---
_quality_app = None

def _get_quality_app():
    """Initialize InsightFace model once on GPU and reuse it."""
    global _quality_app
    if _quality_app is None:
        logger.info("Initializing InsightFace quality checker on GPU...")
        _quality_app = FaceAnalysis(name="buffalo_l")
        _quality_app.prepare(ctx_id=0, det_size=(640, 640))  # ctx_id=0 = GPU
        logger.info("InsightFace quality checker ready on GPU.")
    return _quality_app

def check_face_quality(image, quality_threshold: float = QUALITY_THRESHOLD) -> tuple:
    """
    Check face quality using multiple criteria:
    1. InsightFace detection score
    2. Blur detection (Laplacian variance)
    3. Brightness check
    4. Face pose angle check (yaw, pitch)

    Returns (is_good_quality: bool, quality_score: float)
    """
    try:
        if image is None or image.size == 0:
            return False, 0.0

        # --- CHECK 1: Blur ---
        gray         = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score   = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 30.0:
            logger.debug(f"Rejected — too blurry (blur score: {blur_score:.1f})")
            return False, 0.0

        # --- CHECK 2: Brightness ---
        brightness = np.mean(gray)
        if brightness < 40 or brightness > 230:
            logger.debug(f"Rejected — bad brightness ({brightness:.1f})")
            return False, 0.0

        # --- CHECK 3: InsightFace score + pose ---
        app   = _get_quality_app()
        faces = app.get(image)

        if not faces:
            logger.debug("Rejected — InsightFace found no face.")
            return False, 0.0

        face  = faces[0]
        score = float(face.det_score)

        # --- CHECK 4: Pose angle (yaw and pitch) ---
        if hasattr(face, 'pose'):
            yaw   = abs(face.pose[1])  # left/right rotation
            pitch = abs(face.pose[0])  # up/down rotation
            if yaw > 35 or pitch > 35:
                logger.debug(f"Rejected — bad angle (yaw: {yaw:.1f}, pitch: {pitch:.1f})")
                return False, round(score, 3)

        is_good = score >= quality_threshold
        logger.debug(f"Quality — score: {score:.3f} blur: {blur_score:.1f} brightness: {brightness:.1f}")
        return is_good, round(score, 3)

    except Exception as e:
        logger.error(f"Face quality check failed: {e}")
        return False, 0.0


def load_yolo_model():
    """Load YOLO model on GPU if available, else CPU."""
    use_cuda = False
    if torch.cuda.is_available():
        try:
            torch.zeros(1).cuda()
            use_cuda = True
            logger.info("CUDA is available — using GPU.")
        except Exception:
            logger.warning("CUDA available but incompatible — falling back to CPU.")
    else:
        logger.info("CUDA not available — using CPU.")

    try:
        model = YOLO(MODEL_PATH)
        model = model.to('cuda' if use_cuda else 'cpu')
        logger.info("YOLO model loaded successfully.")
        return model, use_cuda
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
        return None, False


def open_camera_stream(camera_config: dict, stop_event, calendar_id: int):
    """
    Open camera stream, run YOLO face detection, save face crops.
    Works for both webcam and IP camera.
    """
    model, use_cuda = load_yolo_model()
    if model is None:
        return

    face_crops_dir, full_frames_dir, pkl_dir = create_dataset_folders(calendar_id)
    if not face_crops_dir:
        return

    cam_type = camera_config.get("type")

    # --- Build capture source ---
    if cam_type == "ipcam":
        ip       = camera_config.get("ip")
        username = camera_config.get("username")
        password = camera_config.get("password")
        if not all([ip, username, password]):
            logger.error("Missing IP camera credentials.")
            return
        capture_source  = f"rtsp://{username}:{password}@{ip}:554/Stream1"
        capture_backend = cv2.CAP_FFMPEG
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        logger.info(f"Connecting to IP camera: {capture_source}")

    elif cam_type == "webcam":
        device_path = camera_config.get("device_path")
        device_id   = camera_config.get("device_id")
        if device_path:
            capture_source  = device_path
            capture_backend = cv2.CAP_V4L2
        elif device_id is not None:
            capture_source  = device_id
            capture_backend = cv2.CAP_ANY
        else:
            logger.error("Missing webcam device path or ID.")
            return
        logger.info(f"Connecting to webcam: {capture_source}")

    else:
        logger.error(f"Unknown camera type: {cam_type}")
        return

    # --- Main capture loop ---
    while not stop_event.is_set():
        cap = cv2.VideoCapture(capture_source, capture_backend)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if cam_type == "webcam":
            cap.set(cv2.CAP_PROP_FPS, 30)
        else:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            if cam_type == "ipcam":
                logger.warning(f"Cannot open IP camera — retrying in 5 seconds...")
                time.sleep(5)
                continue
            else:
                logger.error(f"Cannot open webcam: {capture_source}")
                return

        logger.info(f"Connected to {cam_type} — running face detection...")

        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to grab frame.")
                if cam_type == "ipcam":
                    break  # reconnect
                else:
                    cap.release()
                    return

            # --- YOLO detection ---
            try:
                results = model.predict(
                    source=frame,
                    show=False,
                    conf=0.4,
                    device='cuda' if use_cuda else 'cpu'
                )
            except Exception as e:
                logger.error(f"YOLO prediction failed: {e}")
                continue

            for box in results[0].boxes:
                conf = float(box.conf[0])
                if conf < 0.70:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                # Add padding
                w, h = frame.shape[1], frame.shape[0]
                x_pad = int((x2 - x1) * PADDING_PERCENT)
                y_pad = int((y2 - y1) * PADDING_PERCENT)
                x1 = max(0, x1 - x_pad)
                y1 = max(0, y1 - y_pad)
                x2 = min(w, x2 + x_pad)
                y2 = min(h, y2 + y_pad)

                face_crop = frame[y1:y2, x1:x2]
                if face_crop.size == 0:
                    continue

                is_good, score = check_face_quality(face_crop, QUALITY_THRESHOLD)

                # ← ADD THIS LINE
                logger.info(f"Face detected — YOLO conf: {conf:.3f} — quality score: {score} — good: {is_good}")

                if is_good:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    face_path = os.path.join(face_crops_dir, f"face_{timestamp}.jpg")
                    frame_path = os.path.join(full_frames_dir, f"frame_{timestamp}.jpg")

                    cv2.imwrite(face_path, face_crop, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    os.chmod(face_path, 0o666)
                    os.chmod(frame_path, 0o666)

                    logger.info(f"Saved face (quality: {score}): face_{timestamp}.jpg")
                else:
                    logger.debug(f"Skipped low quality face (score: {score})")

                break  # one face per frame

        cap.release()