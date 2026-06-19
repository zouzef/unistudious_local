# services/calendar_service.py

from datetime import datetime
from services.client import FlaskClient
from utils.logger import logger


DATE_FORMATS = [
    "%a, %d %b %Y %H:%M:%S %Z",   # Mon, 01 Jan 2026 08:00:00 GMT
    "%Y-%m-%dT%H:%M:%S",           # 2026-01-01T08:00:00
    "%Y-%m-%d %H:%M:%S",           # 2026-01-01 08:00:00
]

def parse_datetime(value: str) -> datetime | None:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    # ← fixed: was inside the loop before, never executed
    logger.warning(f"Could not parse datetime: '{value}'")
    return None


def get_all_calendars(client: FlaskClient) -> list:
	"""Fetch and parse all calendar sessions from Flask server """
	try:
		response = client.get("/get-all-calender")
		raw_sessions = response.json().get("data",[])
		sessions = []
		for s in raw_sessions:
			start = parse_datetime(s.get("start",""))
			end = parse_datetime(s.get("end",""))
			if not start or not end :
				logger.warning(f"Skipping sessions {s.get('id')} - invalid dates.")
				continue

			sessions.append({
				"id":s.get("id"),
				"roomId":s.get("roomId"),
				"startTime":start,
				"endTime":end,
			})
		logger.info(f"Fetched {len(sessions)} valid session(s).")
		return sessions
	except Exception as e:
		logger.error(f"Failed to fetch calendars: {e}")
		return []
