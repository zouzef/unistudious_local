import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

def send_create_camera_api(settings, payload):
	pass

def _send_update_camera_api(settings,payload,cameraId):
	pass

def _send_delete_camera_api(settings, cameraId):
	pass


def push_cameraAdd(db, settings, row):
	pass

def push_cameraUpdate(db, settings, row):
	pass

def push_cameraDelete(db, settings, row):
	pass