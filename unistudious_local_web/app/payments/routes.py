# app/payments/routes.py
from flask import Blueprint, render_template,request, jsonify, session, redirect, url_for
from app.payments.service import(
	get_paymet_session_service

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
			"Message":f"Error: {e} coming from sever"
		}),500
