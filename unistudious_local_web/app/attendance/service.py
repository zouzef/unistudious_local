# app/attendance/service.py
import requests
from flask import current_app
from datetime import datetime


def get_attendance_by_calendar(calendar_id: int) -> list:
	"""Get attendance for a calendar"""
	url = f"{current_app.config['BASE_URL']}get-attendance/{calendar_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		response.raise_for_status()
		return response.json().get('attendance', [])
	except Exception as e:
		print(f"[ATTENDANCE ERROR] get_attendance_by_calendar: {e}")
		return []

def get_list_student(calendar_id: int) -> list:
	"""Get list of students for the calendar"""
	url = f"{current_app.config['BASE_URL']}list-add-student-attendance/{calendar_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		response.raise_for_status()
		return response.json().get('users', [])
	except Exception as e:
		print(f"[ATTENDANCE ERROR] get_list_student: {e}")
		return []

def update_attendance_status(attendance_id: int, status: int) -> tuple:
	"""Update attendance status"""
	url = f"{current_app.config['BASE_URL']}update-attendance-student/{attendance_id}"
	try:
		payload = {"status": status == 1}
		response = requests.post(
			url, json=payload,
			headers={'Content-Type': 'application/json'},
			verify=False, timeout=10
		)
		if response.status_code == 200:
			return True, "Attendance updated successfully"
		else:
			return False, "Failed to update attendance"
	except Exception as e:
		print(f"[ATTENDANCE ERROR] update_attendance_status: {e}")
		return False, "Connection error"

def update_attendance_note(attendance_id: int, note: str) -> tuple:
	"""Update attendance note"""
	url = f"{current_app.config['BASE_URL']}update-attendance-note/{attendance_id}"
	try:
		payload = {"note": note}
		response = requests.post(url, json=payload, verify=False, timeout=10)
		if response.status_code == 200:
			return True, "Note updated successfully"
		else:
			return False, "Failed to update note"
	except Exception as e:
		print(f"[ATTENDANCE ERROR] update_attendance_note: {e}")
		return False, "Connection error"

def reset_attendance(calendar_id: int) -> tuple:
	"""Reset attendance for calendar"""
	url = f"{current_app.config['BASE_URL']}reset_attendance/{calendar_id}"
	try:
		response = requests.post(url, verify=False, timeout=10)
		response.raise_for_status()
		if response.status_code == 200:
			return True, "Attendance reset successfully"
		return False, "Failed to reset attendance"
	except Exception as e:
		print(f"[ATTENDANCE ERROR] reset_attendance: {e}")
		return False, "Connection error"

def get_attendance_statistics(calendar_id: int) -> dict:
	"""Get attendance statistics"""
	url = f"{current_app.config['BASE_URL']}attendance-statistics/{calendar_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		response.raise_for_status()
		return response.json()
	except Exception as e:
		print(f"[ATTENDANCE ERROR] get_attendance_statistics: {e}")
		return {}

def get_attendance_page_data(calendar_id: int) -> dict:
	"""Aggregate all data needed for attendance presence page"""
	from app.calendar.service import get_calendar_by_id

	calendar = get_calendar_by_id(calendar_id)

	# Parse datetime strings
	for field in ['start_time', 'end_time']:
		if calendar and isinstance(calendar.get(field), str):
			try:
				calendar[field] = datetime.strptime(
					calendar[field],
					'%a, %d %b %Y %H:%M:%S %Z'
				)
			except (ValueError, TypeError):
				calendar[field] = None

	return {
		"calender_detail": calendar,
		"attendance": get_attendance_by_calendar(calendar_id),
		"student": get_list_student(calendar_id),
	}