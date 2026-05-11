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
				SELECT p.id, p.account_id, p.session_id, p.user_id, p.type, p.type_date, 
				p.type_number_session, p.date_payment, p.status, p.amount, p.created_by, p.price, 
				p.description, p.forcing, p.enabled, p.created_at, p.timestamp, p.updated_at, p.uuid, u.username ,
				s.name
				FROM payment_session p, user u, session s
				WHERE session_id = %s AND p.enabled = 1 AND p.user_id = u.id AND s.id = p.session_id
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


@payment_bp.route('/update_payment_session/<int:payment_id>', methods=['POST'])
def update_payment_session(payment_id):
    try:
        data = request.get_json()
        amount = data.get('amount')
        user_id = data.get('user_id')
        session_id = data.get('session_id')

        if not amount or not user_id or not session_id:
            return jsonify({"Message": "amount and user_id are required"}), 400

        # Check payment exists
        query = "SELECT count(*) AS nbr FROM payment_session WHERE id = %s AND user_id = %s"
        result = Database.execute_query(query, (payment_id, user_id), fetch=True)
        if result[0]['nbr'] == 0:
            return jsonify({"Message": "There is no payment session with this id"}), 404

        # ✅ Fetch old data BEFORE updating
        query = "SELECT * FROM payment_session WHERE id = %s AND user_id = %s"
        old_record = Database.execute_query(query, (payment_id, user_id), fetch=True)
        old_data = json.dumps(old_record[0], default=str)

        # Perform the update
        query = "UPDATE payment_session SET amount = %s WHERE id = %s AND user_id = %s"
        result = Database.execute_query(query, (amount, payment_id, user_id), fetch=False)

        if result:
            # ✅ Build new data snapshot
            new_data = json.dumps({**old_record[0], "price": amount}, default=str)

            # ✅ Insert into audit table
            audit_query = """
                INSERT INTO payment_session_audit (action_type, old_data, new_data)
                VALUES (%s, %s, %s)
            """
            Database.execute_query(
                audit_query,
                ('UPDATE', old_data, new_data),
                fetch=False
            )

            return jsonify({"Message": "Amount updated successfully"}), 200
        else:
            return jsonify({"Message": "Amount update failed"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500

@payment_bp.route('/get_payment_session_user/<int:session_id>/<int:user_id>')
def get_payment_session_user(session_id,user_id):
	try:
		query="""
		"""
		return jsonify({
			"Message":"Success"
		}),200
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500
