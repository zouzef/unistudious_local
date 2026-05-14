# config.py
import urllib3
from datetime import timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Config:
    # ==========================================
    # CORE
    # ==========================================
    SECRET_KEY = 'a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5'
    TEMPLATE_FOLDER = "../template"

    # ==========================================
    # EXTERNAL API
    # ==========================================
    BASE_URL = " https://192.168.1.249:5004/scl/"
    REQUEST_TIMEOUT = 10
    VERIFY_SSL = False

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