# app/payments/routes.py
from csv import excel_tab

from flask import Blueprint, render_template,request, jsonify, session, redirect, url_for
from app.payments.service import(
	get_paymet_session_service,
	update_payment_service,
	get_payment_user_info_service,
	update_payment_user_service

)

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/api/get_payment_session/<int:session_id>', methods=['GET'])
def get_payment_session(session_id):
	try:
		status,response = get_paymet_session_service(session_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500


@payment_bp.route('/api/get_payment_user_info_service/<int:session_id>/<int:user_id>')
def get_payment_user_info(session_id,user_id):
	try:
		status,response = get_payment_user_info_service(user_id,session_id)
		print(response)
		if status :
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		})


@payment_bp.route('/api/update_payment_session/<int:payment_session>',methods=['POST'])
def update_payment_session(payment_session):
	try:
		data = request.get_json()
		status,response = update_payment_service(payment_session,data)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({"Message": f"Error {e} coming from backend"}), 500


@payment_bp.route('/api/update_payment_session_user/<int:payment_id>/<int:session_id>/<int:user_id>',methods=['POST'])
def update_payment_user(payment_id,session_id,user_id):
	try:
		data = request.get_json()
		status,response = update_payment_user_service(payment_id,session_id,user_id,data)
		print("status coming from the server: ",status)
		print("response coming from the server: ",response)
		return jsonify({
			"Message":data
		})
	except Exception as e:
		print(f"Error: {e} coming from update_payment_user")
		return jsonify({
			"Message":f"Error: {e} coming from update_payment_user"
		}),500