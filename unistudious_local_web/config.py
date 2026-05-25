# config.py
import urllib3
from datetime import timedelta
from pathlib import Path
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load JSON config file
_config_path = Path(__file__).parent / "config.json"
with open (_config_path, "r") as f:
    _cfg = json.load(f)

class Config:
    # ==========================================
    # CORE
    # ==========================================
    SECRET_KEY = _cfg["core"]["secret_key"]
    TEMPLATE_FOLDER = _cfg["core"]["template_folder"]

    # ==========================================
    # EXTERNAL API
    # ==========================================
    BASE_URL = _cfg["external_api"]["base_url"]
    REQUEST_TIMEOUT = _cfg["external_api"]["request_timeout"]
    VERIFY_SSL = _cfg["external_api"]["verify_ssl"]

    # ==========================================
    # SESSION
    # ==========================================
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ==========================================
    # SERVER
    # ==========================================
    HOST = '0.0.0.0'
    PORT = 5016
    CERTFILE = 'cert.pem'
    KEYFILE = 'key.pem'