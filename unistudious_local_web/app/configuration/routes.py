from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from app.configuration.service import (
	get_account_level_service
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
