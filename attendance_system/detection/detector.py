# detection/detector.py

from multiprocessing import Process, Event
from detection.camera import open_camera_stream
from detection.network import scan_all_devices
from utils.logger import logger


def start_detection_for_calendar(calendar_id: int, room_id: int, cameras: list) -> list:
    """
    Start face detection for a calendar session.
    Creates one process per camera.
    Returns list of process info dicts with process and stop_event.
    """
    logger.info(f"Starting detection for calendar {calendar_id} in room {room_id}...")

    stop_event = Event()
    processes  = []

    # Scan network once if there are any IP cameras
    has_ipcam     = any(cam.get("type") == "ipcam" for cam in cameras)
    mac_to_ip     = {}
    if has_ipcam:
        logger.info("IP camera detected — scanning network...")
        devices   = scan_all_devices()
        mac_to_ip = {dev["mac"].lower(): dev["ip"] for dev in devices}

    for cam in cameras:
        cam_type = cam.get("type")

        if not cam_type:
            logger.warning(f"Skipping camera with missing type: {cam}")
            continue

        if cam_type == "ipcam":
            mac      = cam.get("mac", "").lower()
            username = cam.get("username")
            password = cam.get("password")

            if not all([mac, username, password]):
                logger.warning(f"Skipping IP camera — missing credentials: {cam}")
                continue

            ip = mac_to_ip.get(mac)
            if not ip:
                logger.warning(f"IP not found for MAC {mac} — skipping.")
                continue

            camera_config = {
                "type":     "ipcam",
                "ip":       ip,
                "username": username,
                "password": password,
            }
            logger.info(f"Starting IP camera process — MAC: {mac} IP: {ip}")

        elif cam_type == "webcam":
            device_path = cam.get("mac")  # mac field stores device path for webcams

            if not device_path:
                logger.warning(f"Skipping webcam — missing device path: {cam}")
                continue

            if isinstance(device_path, str) and device_path.startswith("/dev/video"):
                camera_config = {"type": "webcam", "device_path": device_path}
            else:
                try:
                    camera_config = {"type": "webcam", "device_id": int(device_path)}
                except (ValueError, TypeError):
                    camera_config = {"type": "webcam", "device_path": device_path}

            logger.info(f"Starting webcam process — device: {device_path}")

        else:
            logger.warning(f"Unknown camera type: {cam_type} — skipping.")
            continue

        p = Process(
            target=open_camera_stream,
            args=(camera_config, stop_event, calendar_id)
        )
        p.start()
        processes.append({
            "process":    p,
            "stop_event": stop_event,
            "camera":     cam.get("name", "unknown")
        })

    logger.info(f"Started {len(processes)} detection process(es) for calendar {calendar_id}.")
    return processes, stop_event


def stop_detection_for_calendar(calendar_id: int, processes: list, stop_event):
    """Stop all detection processes for a calendar session."""
    logger.info(f"Stopping detection for calendar {calendar_id}...")
    stop_event.set()
    for proc_info in processes:
        proc_info["process"].join(timeout=5)
        if proc_info["process"].is_alive():
            proc_info["process"].terminate()
            logger.warning(f"Force terminated process for camera {proc_info['camera']}.")
    logger.info(f"All detection processes stopped for calendar {calendar_id}.")