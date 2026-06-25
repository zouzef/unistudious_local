# detection/detector.py


from multiprocessing import Process, Event, Queue
from detection.camera import open_camera_stream
from detection.network import scan_all_devices
from detection.recognition_worker import recognition_worker
from utils.logger import logger


def start_detection_for_calendar(calendar_id: int, room_id: int, cameras: list, attendances: list, client, recognition_queue) -> tuple:
    """
    Start face detection for a calendar session.
    Creates one process per camera + one recognition worker process.
    Returns (processes, stop_event, recognition_queue)
    """
    logger.info(f"Starting detection for calendar {calendar_id} in room {room_id}...")

    stop_event = Event()
    recognition_queue = Queue(maxsize=50)
    processes          = []

    # Scan network once if there are any IP cameras
    has_ipcam = any(cam.get("type") == "ipcam" for cam in cameras)
    mac_to_ip = {}
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
            device_path = cam.get("mac")

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

        # ✅ Pass recognition_queue to each camera process
        p = Process(
            target=open_camera_stream,
            args=(camera_config, stop_event, calendar_id, recognition_queue)
        )
        p.start()
        processes.append({
            "process":    p,
            "stop_event": stop_event,
            "camera":     cam.get("name", "unknown")
        })

    # ✅ Start ONE recognition worker per calendar
    recognition_process = Process(
        target=recognition_worker,
        args=(recognition_queue, stop_event, attendances, calendar_id, client)
    )
    recognition_process.start()
    processes.append({
        "process":    recognition_process,
        "stop_event": stop_event,
        "camera":     "recognition_worker"
    })

    logger.info(f"Started {len(processes)} process(es) for calendar {calendar_id} ({len(processes)-1} camera(s) + 1 recognition worker).")
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