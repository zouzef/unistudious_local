from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from app.configuration.service import (
	get_account_level_service,
	get_level_service,
	create_account_level_service,
	delete_account_level_service,
	view_account_level_service,
	update_account_level_servie,
	get_account_section_service,
	create_account_section_service,
	delete_account_section_service,
	update_account_section_service,
	view_account_section_service

)

configuration_bp = Blueprint('configuration',__name__)

@configuration_bp.route('/api/get_all_account_level/<int:account_id>',methods=['GET'])
def get_account_level(account_id):
	try:
		status,response = get_account_level_service(account_id)
		if status :
			return jsonify(response.json()),response.status_code
		else:
			return jsonify(response.json()),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})


@configuration_bp.route('/api/create_account_config/<int:account_id>', methods=['POST'])
def create_account_config(account_id):
	try:
		data = request.get_json()
		status, response = create_account_level_service(data, account_id)
		return jsonify(response.json()), status  # 👈 use .json() and return status directly
	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@configuration_bp.route('/api/delete_account_config/<int:account_id>/<int:account_level_id>',methods=['POST'])
def delete_account_level(account_id,account_level_id):
	try:
		status,response = delete_account_level_service(account_id,account_level_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend "
		}),500

@configuration_bp.route('/api/view_account_config/<int:account_level_id>',methods=['GET'])
def view_account_config(account_level_id):
	try:
		status,response = view_account_level_service(account_level_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@configuration_bp.route('/api/update_account_config/<int:account_level_id>',methods=['POST'])
def update_account_config(account_level_id):
	try:
		data = request.get_json()
		status,response= update_account_level_servie(data,account_level_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/get_all_level',methods=['GET'])
def get_all_level():
	try:
		status,response = get_level_service()
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500


@configuration_bp.route('/api/get_all_account_section/<int:account_id>',methods=['GET'])
def get_all_section_config(account_id):
	try:
		status,response = get_account_section_service(account_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/create_account_section/<int:account_id>',methods=['POST'])
def create_account_section(account_id):
	try:
		data=request.get_json()
		status,response = create_account_section_service(data,account_id)
		return jsonify(response.json()).response.status_code()
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/delete_account_section/<int:account_section_id>',methods=['POST'])
def delete_account_section(account_section_id):
	try:
		status,response = delete_account_section_service(account_section_id)
		return jsonify(response.json()),response.status_code()
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/update_account_section/<int:account_section_id>',methods=['POST'])
def update_account_section(account_section_id):
	try:
		data = request.get_json()
		status,response = update_account_section_service(data,account_section_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/view_account_section/<int:account_section_id>',methods=['GET'])
def view_account_section(account_section_id):
	try:
		status,response = view_account_section_service(account_section_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

