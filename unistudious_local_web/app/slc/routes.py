from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
import os
import base64
from app.slc.service import(
	get_slc_info_service,
	get_list_camera_service,
	create_camera_service,
	update_camera_service,
	create_tablet_service,
	update_tablet_service,
	delete_tablet_service,
	fetch_all_tablet_service,
	fetch_room_service,
	view_tablet_service,
	delete_camera_service,


)

slc_bp = Blueprint('slc', __name__)


@slc_bp.route('/api/get_slc_info/<int:account_id>', methods=['GET'])
def get_slc_info(account_id):
    try:
        status, response, status_code = get_slc_info_service(account_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500



# ================================================ CAMERA backend endpoints ================================================
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

@slc_bp.route('/api/update_camera/<int:camera_id>',methods=['POST'])
def update_camera(camera_id):
	try:
		data = request.get_json()
		status,response = update_camera_service(data,camera_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		print(e)
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@slc_bp.route('/api/delete_camera/<int:camera_id>',methods=['POST'])
def delete_camera(camera_id):
	try:
		status,response = delete_camera_service(camera_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend "
		})



# ================================================ TABLET backend endpoints ================================================
@slc_bp.route('/api/create_tablet',methods=['POST'])
def create_tablet():
	try:
		data = request.get_json()
		status,response = create_tablet_service(data)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@slc_bp.route('/api/update_tablet/<int:tablet_id>',methods=['POST'])
def update_tablet(tablet_id):
	try:
		data = request.get_json()
		status,response = update_tablet_service(data,tablet_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@slc_bp.route('/api/delete_tablet/<int:tablet_id>',methods=['POST'])
def delete_tablet(tablet_id):
	try:
		status,response = delete_tablet_service(tablet_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@slc_bp.route('/api/get_all_tablet',methods=['GET'])
def get_all_tablet():
	try:
		status,response = fetch_all_tablet_service()
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400


	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@slc_bp.route('/api/view_tablet_info/<int:tablet_id>',methods=['GET'])
def view_tablet_info(tablet_id):
	try:
		status,response = view_tablet_service(tablet_id)
		if status:
			return jsonify(response),200
		else:
			return  jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend "
		})


# ================================================ Room backend endpoints ================================================
@slc_bp.route('/api/get_room',methods=['GET'])
def get_room():
	try:
		status,response = fetch_room_service()
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500


