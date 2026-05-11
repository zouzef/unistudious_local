# app/payments/routes.py
from csv import excel_tab

from flask import Blueprint, render_template,request, jsonify, session, redirect, url_for
from app.payments.service import(
	get_paymet_session_service,
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


@payment_bp.route('/api/update_payment_session/<int:payment_session>',methods=['POST'])
def update_payment_session(payment_session):
	try:
		data = request.get_json()
		status,response = update_payment_user_service(payment_session,data)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({"Message": f"Error {e} coming from backend"}), 500
