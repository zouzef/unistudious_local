# test_services.py
import threading
from multiprocessing import Event
from detection.camera import open_camera_stream, check_face_quality
import cv2

# First test quality checker alone
print("Testing quality checker...")
cap = cv2.VideoCapture("/dev/video0")
ret, frame = cap.read()
cap.release()

if ret:
    is_good, score = check_face_quality(frame)
    print(f"Quality check result: is_good={is_good}, score={score}")
else:
    print("❌ Could not grab frame for quality test")

# Now test full camera stream
stop_event = Event()

def stop_after(seconds):
    import time
    time.sleep(seconds)
    stop_event.set()
    print("✅ Stop event set.")

threading.Thread(target=stop_after, args=(15,)).start()

print("Opening camera for 15 seconds...")
open_camera_stream(
    {"type": "webcam", "device_path": "/dev/video0"},
    stop_event,
    calendar_id=99999
)
print("✅ Done — check dataset/session_9999/face_crops/")