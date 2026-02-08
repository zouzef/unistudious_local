from flask import Blueprint, jsonify, request
from datetime import datetime
from services.calender_service import (
	fetch_calender_room,
	fetch_group_session,
	fetch_room,
	fetch_session,
	fetch_teacher
)


calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.route('/get-calendar-room/<int:room_id>',methods=['GET'])
def get_calender_room(room_id):

	try:
		calendar = fetch_calender_room(room_id)
		return jsonify(calendar)
	except Exception as e:
		print(f"Error {e} coming from get calender room")
		return jsonify({"status": "error", "message": str(e)}), 500


@calendar_bp.route("/get-group-session/<int:account_id>/<int:session_id>", methods=['GET'])
def get_group_session(account_id, session_id):
	try:
		group_data = fetch_group_session(account_id, session_id)
		if group_data:
			return jsonify(group_data), 200
		else:
			return jsonify({"Message": "No data found or error in params"}), 404
	except Exception as e:
		# Return 500 status code for server errors
		return jsonify({"Message": f"Error: {str(e)}"}), 500


@calendar_bp.route("/get-room-local/<int:local_id>",methods=['GET'])
def getRoomLocal(local_id):
	try:
		room_data = fetch_room(local_id)
		if room_data:
			return jsonify(room_data),200

		else:
			return jsonify({"Message": "No data found or error in params"}),404
	except Exception as e:
		return jsonify({"Message": f"Error: {str(e)}"}),500

@calendar_bp.route('/get-session/<int:account_id>',methods=['GET'])
def get_session(account_id):
	try:
		session_data = fetch_session(account_id)
		if session_data:
			return jsonify(session_data),200
		else:
			return jsonify({"Message": "No data found or error in params"}),404
	except Exception as e:
		return jsonify({"Message": f"Error: {str(e)}"}),500

@calendar_bp.route('/get-teacher/<int:session_id>',methods=['GET'])
def get_Teacher_Session(session_id):
	try:
		teacher_data = fetch_teacher(session_id)

		print(teacher_data)
		if teacher_data:
			return jsonify(teacher_data),200
		else:
			return jsonify({"Message":"No data found or Error in parms"}),404
	except Exception as e:
		return jsonify({"Message":f"Error: {str(e)}"}),500
