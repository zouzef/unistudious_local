from flask import Blueprint, jsonify, request
from datetime import datetime
from services.subject_service import (
    fetch_subject
)


subject_bp = Blueprint('subject',__name__)

@subject_bp.route('/api/get-subjects',methods=['GET'])
def api_get_subject():
    try:
        subject_data = fetch_subject()
        if subject_data:
            return jsonify({
                "data": subject_data
            }), 200
        else:
            return jsonify({
                "Message":"There is no subject"
            }),404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "Message":f"Error: {e} coming from Server"
        }),500