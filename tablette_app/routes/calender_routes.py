from flask import current_app,Blueprint, jsonify, request
from datetime import datetime
from services.calender_service import (
	fetch_calender_room,
	fetch_group_session,
	fetch_room,
	fetch_session,
	fetch_teacher,
	request_calander,
	fetch_calander_request

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


@calendar_bp.route('/create-calander_request/<int:session_id>', methods=['POST'])
def create_calander(session_id):
	try:
		calander_data = request.get_json()

		if not calander_data:
			return jsonify({
				"Message": "Error: No data provided",
				"Status": "error"
			}), 400

		# List of required fields
		required_fields = [
			'session_id',
			'group_id',
			'type',
			'room_id',
			'subject_id',
			'user_id',
			'duplicate',
			'start_time',
			'end_time',
			'end_date',
			'description',
			'account_id',
			'tag'
		]

		# Check if any required field is None or missing
		missing_or_none_fields = []

		for field in required_fields:
			if field not in calander_data or calander_data[field] is None:
				missing_or_none_fields.append(field)

		if missing_or_none_fields:
			return jsonify({
				"Message": f"Error: Missing or None values for fields: {', '.join(missing_or_none_fields)}",
				"Status": "error"
			}), 400

		# Process the calendar data
		response = request_calander(calander_data)

		if response:
			# ✅ **NEW: Emit WebSocket event after successful creation**
			try:
				room_id = calander_data.get('room_id')

				# Get the updated calendar data for this room
				updated_calendar_data = fetch_calander_request(room_id)

				# Get socketio instance from current_app
				from flask import current_app
				socketio = current_app.extensions.get('socketio')

				if socketio and updated_calendar_data:
					socketio.emit('calendar_update',
								  {
									  'room_id': room_id,
									  'data': updated_calendar_data,
									  'message': 'New calendar request added from tablet',
									  'timestamp': datetime.now().isoformat()
								  },
								  room=f'calendar_room_{room_id}'
								  )
					print(f'✅ Emitted calendar_update to calendar_room_{room_id}')
			except Exception as ws_error:
				print(f'⚠️ WebSocket emit failed: {ws_error}')
			# Don't fail the request if WebSocket fails

			return jsonify({
				"Message": "Success",
				"Status": "success"
			}), 200
		else:
			return jsonify({
				"Message": "Error in create calendar",
				"Status": "error"
			}), 400

	except Exception as e:
		print(f"Error in create_calander: {str(e)}")

		return jsonify({
			"Message": f"Error: {str(e)}",
			"Status": "error"
		}), 500


@calendar_bp.route('/get-calander-request/<int:room_id>', methods=['GET'])
def get_calander_request(room_id):
    try:
       calander_data = fetch_calander_request(room_id)

       if calander_data:
          # Just return the data directly, don't wrap it again
          return jsonify(calander_data), 200
       else:
          return jsonify({
             "Message": "No calendar requests found",
             "data": []
          }), 404

    except Exception as e:
       print(f"Error in get_calander_request: {str(e)}")
       return jsonify({
          "Message": f"Error: {str(e)} coming from get_calander",
          "data": []
       }), 500