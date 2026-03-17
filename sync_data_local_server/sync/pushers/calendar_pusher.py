import sys
import os
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.auth import get_token

# API unistudious ADD calander
def _send_calendar(settings, payload):
	"""Send calendar data to remote API."""
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-calendar-normal-group"

		print(f"📡 Sending to remote: {url}")
		print(f"📦 Payload: {payload}")

		# ✅ Correct: use 'data' for form-data (don't set Content-Type header)
		response = requests.post(url, data=payload, headers=headers, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				print(f"❌ Invalid JSON response: {response.text}")
				return False, None

			remote_id = response_data.get('attendance', {}).get('id')
			print(f"✅ Remote API success: {response_data}")
			return True, remote_id
		else:
			print(f"❌ Remote API returned {response.status_code}: {response.text}")
			return False, None

	except requests.exceptions.Timeout:
		print(f"❌ Request timeout (10s)")
		return False, None
	except Exception as e:
		print(f"❌ Remote API error: {str(e)}")  # ✅ Now shows actual error
		return False, None


def _send_update_calander(settings, calendar_id, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/edit-calendar/{calendar_id}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				print(f"✅ Remote API success: {response_data}")
				return True
			except Exception:
				print(f"❌ Invalid JSON response: {response.text}")
				return False
		else:
			print(f"❌ Remote API returned {response.status_code}: {response.text}")
			return False

	except Exception as e:
		print(f"❌ Remote API error: {str(e)}")  # ✅ Don't reference response
		return False


def _send_delete_calander(settings, calendar_id, payload):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-calendar/{calendar_id}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
				print(f"✅ Remote API success: {response_data}")
				return True
			except Exception:
				print(f"❌ Invalid JSON response: {response.text}")
				return False
		else:  # ✅ Added else block
			print(f"❌ Remote API returned {response.status_code}: {response.text}")
			return False

	except Exception as e:
		print(f"❌ Remote API error: {str(e)}")  # ✅ Don't reference response
		return False