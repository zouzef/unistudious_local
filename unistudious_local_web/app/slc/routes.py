from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
import os
import base64
from app.slc.service import(
	get_slc_info_service,
	get_list_camera_service,
	create_camera_service
)

slc_bp = Blueprint('slc', __name__)


@slc_bp.route('/api/get_slc_info/<int:account_id>',methods=['GET'])
def get_slc_info(account_id):
	try:
		status,response = get_slc_info_service(account_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@slc_bp.route('/api/get_list_camera',methods=['GET'])
def get_list_camera():
	try:
		status,response = get_list_camera_service()
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		})


@slc_bp.route('/api/create_camera',methods=['POST'])
def create_camera():
	try:
		data = request.get_json()
		if not data:
			return jsonify({
				"Message":"There is no data to insert camera"
			}),404
		else:
			status,response = create_camera_service(data)
			if status:
				return jsonify({
					"Message":"Camera created with success! "
				}),200
			else:
				return jsonify({
					"Message":"Camera creation failed"
				}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})