from flask import Blueprint, request, jsonify
import os
import sys
import json
from pathlib import Path
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


#create payment blueprint
payment_bp = Blueprint('payment', __name__ , url_prefix='/scl')

@payment_bp.route('/get_payment_session/<int:session_id>',methods=['GET'])
def get_payment_session(session_id):
	try:
		query = """
			SELECT count(*) AS nbr 
			FROM session WHERE id = %s AND enabled = 1
		"""
		values =(session_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result[0]['nbr']==0:
			return jsonify({
				"Message":"session Not found "
			}),404
		else:
			query ="""
				SELECT id, account_id, session_id, user_id, type, type_date, 
				type_number_session, date_payment, status, amount, created_by, price, 
				description, forcing, enabled, created_at, timestamp, updated_at, uuid
				FROM payment_session
				WHERE session_id = %s AND enabled = 1 
				GROUP BY user_id
				ORDER BY created_at DESC
			"""
			values = (session_id,)
			result = Database.execute_query(query,values,fetch=True)


			return jsonify({
				"Message":"Success",
				"Data":result
			}),200

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from the server"
		}),500