# utils/logger.py

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(LOG_DIR, f"attendance_{datetime.now().strftime('%Y-%m-%d')}.log")

logger = logging.getLogger("attendance_system")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S"
))

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s  %(levelname)-8s  [%(filename)s:%(lineno)d]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

logger.addHandler(console_handler)
logger.addHandler(file_handler)