from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import join_room, leave_room, emit
from websockets import get_socketio
import requests
from nacl.pwhash import verify
from datetime import datetime




# ==========================================
# CONFIGURATION
# ==========================================
dashboard_bp = Blueprint('dashboard', __name__)
BASE_URL = " https://172.28.20.178:5004/scl/"


# ==========================================
# SESSION FUNCTIONS
# ==========================================

def get_session_slc(account_id):
	"""Get all sessions from SLC API"""
	url = f"{BASE_URL}get_session_detail/{account_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		if response.status_code == 200:
			data = response.json()
			sessions = data.get('data', [])
			return sessions
		else:
			print(f"Error: API returned status {response.status_code}")
			return []
	except requests.exceptions.RequestException as e:
		print(f"Error fetching sessions: {e}")
		return []


def get_data_moderateur(account_id):
	"""Get moderator data from SLC API"""
	url = f"{BASE_URL}get_data_moderateur/{account_id}"
	try:
		response = requests.get(url, verify=False, timeout=10)
		response.raise_for_status()
		data = response.json()
		return data.get('data', {})
	except Exception as e:
		print(f"Error: {e}")
		return {}


def get_local(account_id):
	"""Get local details from SLC API"""
	url = f"{BASE_URL}get_local_detail/{account_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			local_detail = data.get('data', [])
			return local_detail
		else:
			print(f"Error: API returned status {response.status_code}")
			return []
	except Exception as e:
		print(f"DEBUG: Error {e}")
		return []


@dashboard_bp.route("/api/get_room/<int:local_id>")
def get_room(local_id):
	"""Get rooms from local"""
	url = f"{BASE_URL}get_room/{local_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			room = data.get("data", [])
			return jsonify({"Message": "Success", "Room": room})
	except Exception as e:
		print(f"Error {e} coming from get_room")
		return jsonify({"Message": f"Error {e}"}), 500


@dashboard_bp.route("/api/get_teacher/<int:session_id>")
def get_teacher(session_id):
	"""Get teachers from session"""
	url = f"{BASE_URL}get_teacher/{session_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			teacher = data.get("data", [])
			return jsonify({"Message": "Success", "teacher": teacher}), 200
		else:
			return jsonify({"Message": "there is no teacher", "Teacher": []}), 404
	except Exception as e:
		print(f"Error {e}")
		return jsonify({"message": f"Error {e} coming from get teacher"}), 500


# ==========================================
# CALENDAR FUNCTIONS
# ==========================================

def get_calander_per_session(account_id, session_id):
	"""Get calendar data for a specific session from SLC API"""
	url = f"{BASE_URL}get_calendar_session/{session_id}/{account_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			calendar = data.get("data", [])
			return calendar
		else:
			print(f"Error: API returned status {response.status_code}")
			return []
	except Exception as e:
		print(f"DEBUG: Error {e} from the local server !!")
		return []


def detail_calender_by_id(calender_id):
	"""Get the detail of the calendar"""
	url = f"{BASE_URL}get_calander_id/{calender_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			calendar = data.get("data", [])
			return calendar
	except Exception as e:
		print(f"DEBUG: Error {e} from the local server !!")
		return []


def get_list_student(calendar_id):
	"""Get list of students for the calendar"""
	url = f"{BASE_URL}list-add-student-attendance/{calendar_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			users = data.get("users", [])
			return users
		else:
			print("there is no user for this attendance")
			return []
	except Exception as e:
		print(f"Problem {e} is coming from the server ")
		return []

# Get calander for every session
@dashboard_bp.route('/dashboard/get_calander_per_session/<int:account_id>/<int:session_id>', methods=['GET'])
def api_get_calendar_per_session(account_id, session_id):
	"""API endpoint to get calendar data as JSON"""
	try:
		calendar = get_calander_per_session(account_id, session_id)
		return jsonify({
			'success': True,
			'data': calendar
		}), 200
	except Exception as e:
		print(f"DEBUG: Error {e}")
		return jsonify({
			'success': False,
			'error': str(e),
			'data': []
		}), 500


# Delete calander
@dashboard_bp.route('/api/delete-calander/<int:session_id>', methods=['DELETE', 'POST'])
def delete_calander(session_id):
	"""Delete calendar interval"""
	url = f"{BASE_URL}deleting_interval/{session_id}"
	try:
		data = request.json

		if not data:
			return jsonify({"message": "No data provided"}), 400

		start_date = data.get('start_date')
		end_date = data.get('end_date')

		if not start_date or not end_date:
			return jsonify({"message": "Error: missing start_date or end_date"}), 400

		try:
			datetime.strptime(start_date, '%Y-%m-%d')
			datetime.strptime(end_date, '%Y-%m-%d')
			start_date_with_time = f"{start_date} 00:00:00"
			end_date_with_time = f"{end_date} 23:59:59"
		except ValueError:
			return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

		response = requests.post(url, json={
			'start_date': start_date_with_time,
			'end_date': end_date_with_time
		}, verify=False)

		if response.status_code == 200:
			return jsonify({
				"message": "Calendar interval deleted successfully",
				"start_date": start_date,
				"end_date": end_date
			}), 200
		else:
			return jsonify({
				"message": "Failed to delete interval from external API",
				"error": response.text,
				"status_code": response.status_code
			}), 400
	except requests.exceptions.RequestException as e:
		return jsonify({"message": "Error connecting to external server", "error": str(e)}), 500
	except Exception as e:
		import traceback
		traceback.print_exc()
		return jsonify({"message": "Internal server error", "error": str(e)}), 500


# Create calander
@dashboard_bp.route('/api/create-calander', methods=['POST'])
def create_calander():
	url = f"{BASE_URL}/create_calander"
	try:
		response = requests.post(url,verify=False)
		response.raise_for_status()

		resp_code = response.status_code
		if resp_code == 201:
			return jsonify({
				"Message":"Succes calander created successfuly"
			}),200
		elif resp_code == 402:
			return response.json()


	except Exception as e:
		print(f"Error {e}: coming from create_calander")
		return jsonify({"Message":"Error coming from server"}),500




def send_calendar_request_notification(socketio, account_id, data):
	try:
		socketio.emit(
			'calendar_notification',
            {
                'title': data.get('title', 'No title'),
                'time': data.get('time', 'No time'),
                'avatar': data.get('avatar', None)
            },
			room=f"admin_{account_id}"  # or your own room logic
		)
		return True
	except:
		return False


# Notification par for the calender-request
@dashboard_bp.route('/api/notify-calendar-request', methods=['POST'])
def notify_calendar_request():
	try:
		notification_data = request.get_json()
		print(notification_data)
		if not notification_data:
			return jsonify({"Message": "No data provided"}), 400

		account_id = notification_data.get('account_id')

		if not account_id:
			return jsonify({"Message": "account_id is required"}), 400

		# Get SocketIO instance
		socketio = get_socketio()

		if socketio:
			# Send notification to connected admin
			success = send_calendar_request_notification(
				socketio,
				account_id,
				notification_data
			)

			if success:
				print(f"✅ Notification broadcasted to admin {account_id}")
				return jsonify({
					"Message": "Notification sent successfully",
					"account_id": account_id
				}), 200
			else:
				print(f"⚠️ Admin {account_id} is not connected")
				return jsonify({
					"Message": "Admin not connected, notification saved",
					"account_id": account_id
				}), 200
		else:
			print("❌ SocketIO not initialized")
			return jsonify({"Message": "WebSocket not available"}), 500

	except Exception as e:
		print(f"❌ Error in notify_calendar_request: {e}")
		return jsonify({
			"Message": "Error processing notification",
			"error": str(e)
		}), 500


# ==========================================
# GROUP FUNCTIONS
# ==========================================

@dashboard_bp.route('/api/get-group/<int:session_id>/<int:account_id>')
def get_group_api(session_id, account_id):
	"""Get groups with students"""
	url = f"{BASE_URL}get-group/{account_id}/{session_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			groups = data.get("data", [])
			return jsonify({"Message": "Success", "data": groups}), 200
		else:
			return jsonify({"Message": "Error", "data": []}), 400
	except Exception as e:
		print(f"Error coming from get_group_route {e}")
		return jsonify({"Message": "Error"}), 500


@dashboard_bp.route('/api/delete-group/<int:id_group>', methods=["DELETE"])
def delete_group(id_group):
	url = f"{BASE_URL}/delete-group/{id_group}"
	try:

		response = requests.post(url, verify= False)
		response.raise_for_status()

		if response.status_code==200:
			return jsonify({"Message": "group delete avec succes"}),200
		else:
			return jsonify({"Message":"group not deleted "}),404

	except Exception as e:
		print(f"Error coming from delete_group{e}")
		return jsonify({"Message":"Error coming from server"}),500


# Delete use from group
@dashboard_bp.route('/api/delete_user_f_group/<int:session_id>/<int:user_id>',methods=["POST"])
def delete_user_from_group(session_id, user_id):
	url = f"{BASE_URL}/delete-user-from-group/{session_id}/{user_id}"
	try:
		response = requests.post(url,verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			return jsonify({"Message": "user deletet with success"}),200
		else:
			return jsonify({"Message":"Error in deleting user"}),400


	except Exception as e:
		print(f"Error {e} coming from delete user from group")
		return jsonify({"Message":"Error coming from the server"}),500


@dashboard_bp.route('/api/show_user_not_affected/<int:session_id>/<int:account_id>')
def show_user_not_affected(session_id, account_id):
	"""Get users not affected to any group"""
	url = f"{BASE_URL}user_not_affected/{session_id}/{account_id}"

	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			user_not_affected = data.get("students", [])
			return jsonify({"Message": "Success", "students": user_not_affected}), 200
		else:
			return jsonify({"Message": "Error", "students": []}), 400
	except Exception as e:
		print(f"Error: {e}")
		return jsonify({"Message": "Error coming from server", "students": []}), 500


@dashboard_bp.route('/api/affect_user/<int:session_id>', methods=["POST"])
def affect_user(session_id):
	"""Affect user to a group"""
	url = f"{BASE_URL}affect_user_group/{session_id}"
	try:
		data = request.get_json()

		if not data:
			return jsonify({"Message": "No data provided"}), 400

		if not data.get("user_id") or not data.get("group_id"):
			return jsonify({"Message": "Missing user_id or group_id"}), 400

		payload = {
			"user_id": data.get("user_id"),
			"group_id": data.get("group_id")
		}

		response = requests.post(url, json=payload, verify=False)
		response.raise_for_status()

		if response.status_code == 200:
			result = response.json()
			return jsonify({"Message": "Success", "data": result}), 200
		else:
			return jsonify({"Message": "Failed to affect student"}), 400

	except requests.exceptions.RequestException as e:
		print(f"Request error {e}")
		return jsonify({"Message": f"Request error: {e}"}), 500
	except Exception as e:
		print(f"Error {e} coming from server")
		return jsonify({"Message": f"Error: {e}"}), 500


@dashboard_bp.route('/api/get_subject_group/<int:account_id>', methods=["GET"])
def get_subject_group(account_id):
	url = f"{BASE_URL}get-subject-account/{account_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		# Return the data directly from the backend
		return jsonify(response.json()), 200

	except requests.exceptions.HTTPError as http_err:
		# Handle HTTP errors (4xx, 5xx)
		print(f"HTTP error in get_subject_group: {http_err}")
		return jsonify({"Message": "Error fetching subject account", "Data": []}), response.status_code

	except requests.exceptions.RequestException as req_err:
		# Handle connection errors
		print(f"Request error in get_subject_group: {req_err}")
		return jsonify({"Message": "Error connecting to server", "Data": []}), 500

	except Exception as e:
		# Handle any other errors
		print(f"Error in get_subject_group: {str(e)}")
		return jsonify({"Message": "Internal server error", "Data": []}), 500


@dashboard_bp.route('/api/create_group/<int:session_id>', methods=['POST'])
def create_group(session_id):
	url = f"{BASE_URL}create_group/{session_id}"
	try:
		# Get JSON data from the request
		data = request.json

		# Validate required fields
		if not data:
			return jsonify({"Message": "No data provided"}), 400

		# Send POST request with data
		response = requests.post(url, json=data, verify=False)
		response.raise_for_status()

		# Return the actual response from the backend
		return jsonify(response.json()), response.status_code

	except requests.exceptions.HTTPError as http_err:
		print(f"HTTP error in create_group: {http_err}")
		if response:
			return jsonify(response.json()), response.status_code
		return jsonify({"Message": "HTTP error occurred"}), 500

	except requests.exceptions.RequestException as req_err:
		print(f"Request error in create_group: {req_err}")
		return jsonify({"Message": "Error connecting to server"}), 500

	except Exception as e:
		print(f"Error in create_group: {str(e)}")
		return jsonify({"Message": "Error coming from server", "Error": str(e)}), 500


# ==========================================
# ATTENDANCE FUNCTIONS
# ==========================================

def attendance_by_id(calendar_id):
	"""Get the attendance of the calendar"""
	url = f"{BASE_URL}get-attendance/{calendar_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			attendance = data.get("attendance", [])
			return attendance
		else:
			print("there is no attendance for this calendar")
			return []
	except Exception as e:
		print("Error coming from server")
		return []


@dashboard_bp.route("/api/change-status/<int:status>/<int:attendance_id>")
def update_attendance(status, attendance_id):
	"""Change attendance status"""
	url = f"{BASE_URL}update-attendance-student/{attendance_id}"
	try:
		is_present = status == 1
		payload = {
			"status": is_present
		}
		print(payload)
		response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, verify=False)
		if response.status_code == 200:
			print("response==200")
			return jsonify({
				"success": True,
				"message": "Attendance updated successfully",
				"data": response.json()
			}), 200
		else:
			return jsonify({
				"success": False,
				"message": "Failed to update attendance",
				"error": response.json() if response.text else "Unknown error",
				"status_code": response.status_code
			}), response.status_code

	except requests.exceptions.ConnectionError as e:
		print(f"Connection Error: {e}")
		return jsonify({
			"success": False,
			"message": "Could not connect to the attendance service"
		}), 500
	except requests.exceptions.Timeout as e:
		print(f"Timeout Error: {e}")
		return jsonify({
			"success": False,
			"message": "Request timed out"
		}), 500
	except Exception as e:
		print(f"Error {e} coming from update_attendance!!")
		return jsonify({
			"success": False,
			"message": "An unexpected error occurred",
			"error": str(e)
		}), 500


@dashboard_bp.route("/api/change-note/<int:attendance_id>", methods=['POST'])
def update_note(attendance_id):
	"""Change attendance note"""
	url = f"{BASE_URL}update-attendance-note/{attendance_id}"

	try:
		# Get the note from the request body
		if request.is_json:
			data = request.get_json()
			note = data.get('note', '')
		else:
			note = request.form.get('note', '')
		payload = {
			"note": note
		}
		response = requests.post(url, json=payload, verify=False)
		if response.status_code == 200:
			return jsonify({
				"success": True,
				"message": "Note updated successfully",
				"data": response.json()
			}), 200
		else:
			return jsonify({
				"success": False,
				"message": "Failed to update note",
				"error": response.json() if response.text else "Unknown error",
				"status_code": response.status_code
			}), response.status_code

	except requests.exceptions.ConnectionError as e:
		print(f"Connection Error: {e}")
		return jsonify({
			"success": False,
			"message": "Could not connect to the attendance service"
		}), 500
	except requests.exceptions.Timeout as e:
		print(f"Timeout Error: {e}")
		return jsonify({
			"success": False,
			"message": "Request timed out"
		}), 500
	except Exception as e:
		print(f"Error {e} coming from update_note!!")
		return jsonify({
			"success": False,
			"message": "An unexpected error occurred",
			"error": str(e)
		}), 500


@dashboard_bp.route("/api/reset-attendance/<int:calander_id>", methods=["post"])
def reset_attendance(calander_id):
	"""Reset attendance"""
	url = f"{BASE_URL}reset_attendance/{calander_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			return jsonify({"Message": "Operation reset success! "}), 200
		else:
			return jsonify({"Message": "Error coming from server"}), 500
	except Exception as e:
		print("Error coming from reset_attendance")
		return jsonify({"Message": f"Error {e}"}), 500


@dashboard_bp.route("/api/get-statistic/<int:calander_id>", methods=["GET"])
def get_calender_statistic(calander_id):
	"""Get attendance statistics"""
	url = f"{BASE_URL}attendance-statistics/{calander_id}"
	try:
		response = requests.get(url, verify=False)
		response.raise_for_status()
		if response.status_code == 200:
			data = response.json()
			return jsonify({"Message": "succes", "data": data}), 200
		else:
			return jsonify({"Message": "Error coming from server"}), 500
	except Exception as e:
		print(f"Error:{e} coming from get statistic")
		return jsonify({"Message": "Error "}), 500


# ==========================================
# DASHBOARD ROUTES
# ==========================================

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
	"""Main dashboard page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	account_id = session.get('account_id', 3)
	sessions = get_session_slc(account_id)
	data_modera = get_data_moderateur(account_id)
	local_details = get_local(account_id)

	return render_template('index.html',
						   sessions=sessions,
						   data_modera=data_modera,
						   local_details=local_details,
						   page='home')


# ==========================================
# SESSION ROUTES
# ==========================================

@dashboard_bp.route('/dashboard/show-session')
def show_sessions():
	"""Display all sessions page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	account_id = session.get('account_id', 3)
	sessions = get_session_slc(account_id)

	return render_template('index.html',
						   sessions=sessions,
						   page='show-session')


@dashboard_bp.route('/dashboard/create-session', methods=['GET'])
def create_session():
	"""Create new session page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create-session')


@dashboard_bp.route('/dashboard/show-session-config/<int:id_session>', methods=['GET'])
def show_session_config(id_session):
	"""Session configuration page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	account_id = session.get('account_id', 3)
	calendar_data = get_calander_per_session(account_id, id_session)
	local_details = get_local(account_id)
	sessions = get_session_slc(account_id)
	data_modera = get_data_moderateur(account_id)

	return render_template('index.html',
						   id_session=id_session,
						   account_id=account_id,
						   calendar_data=calendar_data,
						   local_details=local_details,
						   sessions=sessions,
						   data_modera=data_modera,
						   page='session_config')


# ==========================================
# CALENDAR ROUTES
# ==========================================

@dashboard_bp.route('/dashboard/create-session-calendar/<int:id_session>')
def show_create_session_calendar(id_session):
	"""Create/edit session calendar page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   id_session=id_session,
						   page='session_calander')


# ==========================================
# GROUP ROUTES
# ==========================================

@dashboard_bp.route('/dashboard/create-group-user-session/<int:id_session>')
def show_create_group_session(id_session):
	"""Create/edit group for session page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	account_id = session.get('account_id', 3)

	# Get local_id from the local details
	local_details = get_local(account_id)

	# Extract local_id from the first local (or you can let user choose)
	if local_details and len(local_details) > 0:
		local_id = local_details[0].get('id', 1)  # Get the first local's id
	else:
		local_id = 1  # Default fallback

	print(f"account_id: {account_id}")
	print(f"local_id: {local_id}")
	print(f"id_session: {id_session}")

	return render_template('index.html',
						   id_session=id_session,
						   account_id=account_id,
						   local_id=local_id,
						   page='group_user_session')


# ==========================================
# ATTENDANCE ROUTES
# ==========================================

@dashboard_bp.route('/dashboard/show-attendance-sessions/<int:session_id>', methods=['GET'])
def show_attendance_page(session_id):
	"""Show attendance overview for session"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	account_id = session.get('account_id', 3)

	return render_template('index.html',
						   id_session=session_id,
						   account_id=account_id,
						   page='attendance_page')


@dashboard_bp.route('/dashboard/show-attendance-presence/<int:id_calander>')
def show_attendance_presence(id_calander):
	"""Show detailed attendance/presence page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	calender_detail = detail_calender_by_id(id_calander)
	attendance = attendance_by_id(id_calander)
	print(attendance)
	list_student = get_list_student(id_calander)

	# Parse datetime strings if they exist
	if calender_detail and isinstance(calender_detail.get('start_time'), str):
		try:
			calender_detail['start_time'] = datetime.strptime(
				calender_detail['start_time'],
				'%a, %d %b %Y %H:%M:%S %Z'
			)
		except (ValueError, TypeError):
			calender_detail['start_time'] = None

	if calender_detail and isinstance(calender_detail.get('end_time'), str):
		try:
			calender_detail['end_time'] = datetime.strptime(
				calender_detail['end_time'],
				'%a, %d %b %Y %H:%M:%S %Z'
			)
		except (ValueError, TypeError):
			calender_detail['end_time'] = None

	return render_template('index.html',
						   id_calander=id_calander,
						   calender_detail=calender_detail,
						   attendance=attendance,
						   student=list_student,
						   page='show_attendance_presence')


@dashboard_bp.route('/dashboard/show-attendance-unknown-student/<int:calender_id>')
def show_attendance_unknown(calender_id):
	"""Show unknown student"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))
	else:
		return render_template('index.html',
							   calender_id=calender_id,
							   page="show-unknown-student")


# ==========================================
# PAYMENT ROUTES
# ==========================================

@dashboard_bp.route('/dashboard/show-payment-session')
def show_payment_session():
	"""Show all payment sessions"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show-payment-session')


@dashboard_bp.route('/dashboard/show-payment-session-details/<int:session_id>')
def show_payment_session_details(session_id):
	"""Show payment details for specific session"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   session_id=session_id,
						   page='show_payment_session_detail')


@dashboard_bp.route('/dashboard/show-user-session/<int:id_user>/<int:id_session>')
def show_user_session(id_user, id_session):
	"""Show payment details for specific user in session"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   id_user=id_user,
						   id_session=id_session,
						   page='show_payment_user_session')