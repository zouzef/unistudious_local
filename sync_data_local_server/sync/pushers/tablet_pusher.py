import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

def send_create_tablet_api(settings, payload):
	pass

def _send_update_tablet_api(settings,payload,tabletId):
	pass

def _send_delete_tablet_api(settings, tabletId):
	pass


def push_tabletAdd(db, settings, row):
	pass

def push_tabletUpdate(db, settings, row):
	pass

def push_tabletDelete(db, settings, row):
	pass