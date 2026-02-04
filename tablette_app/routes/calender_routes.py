from flask import Blueprint, jsonify, request
from datetime import datetime
from services.calender_service import (
	fetch_calender_room
)


calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.route('/get-calendar-room/<int:room_id>',methods=['GET'])
def get_calender_room(room_id):

	try:
		calendar = fetch_calender_room(room_id)
		print(calendar)
		return jsonify(calendar)
	except Exception as e:
		print(f"Error {e} coming from get calender room")
		return jsonify({"status": "error", "message": str(e)}), 500