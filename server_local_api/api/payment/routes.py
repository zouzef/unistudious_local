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
				p.description, p.forcing, p.enabled, p.created_at, p.timestamp, p.updated_at, p.uuid, u.full_name ,
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


@payment_bp.route('/get_payment_session_user/<int:session_id>/<int:user_id>')
def get_payment_session_user(session_id,user_id):
	try:
		query="""
			SELECT p.id, p.date_payment, p.description, p.status, p.amount, p.type_date,
			u.full_name as username,s.name
			FROM payment_session p,user u, session s
			WHERE session_id = %s AND user_id = %s AND u.id = p.user_id AND s.id = p.session_id AND u.enabled = 1 AND s.enabled = 1 AND p.enabled = 1
		"""
		values =(session_id,user_id)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({"Message":"There is no payment session with this id"}), 404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
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


@payment_bp.route('/update_payment_session_user/<int:session_id>/<int:user_id>/<int:payment_id>', methods=['POST'])
def update_payment_session_user(session_id, user_id, payment_id):
    try:
        data = request.get_json()

        # Check if the payment record exists
        check_query = """
            SELECT COUNT(*) AS nbr 
            FROM payment_session
            WHERE user_id = %s AND session_id = %s AND id = %s 
        """
        result = Database.execute_query(check_query, (user_id, session_id, payment_id), fetch=True)

        if not result or result[0]['nbr'] == 0:
            return jsonify({"Message": "Payment record not found"}), 404

        # Fetch old data BEFORE updating
        old_record_query = """
            SELECT * FROM payment_session
            WHERE user_id = %s AND session_id = %s AND id = %s
        """
        old_record = Database.execute_query(old_record_query, (user_id, session_id, payment_id), fetch=True)
        old_data   = json.dumps(old_record[0], default=str)

        # Build dynamic update query based on provided fields only
        fields = []
        values = []

        # Always update updated_at
        fields.append("updated_at = NOW()")

        if 'amount' in data and data['amount'] is not None:
            fields.append("amount = %s")
            values.append(data['amount'])

        if 'description' in data and data['description'] is not None:
            fields.append("description = %s")
            values.append(data['description'])

        if 'status' in data and data['status'] is not None:
            fields.append("status = %s")
            values.append(data['status'])

        # Only updated_at was added, no real fields to update
        if len(fields) == 1:
            return jsonify({"Message": "No fields to update"}), 400

        # Add WHERE clause values
        values.extend([user_id, session_id, payment_id])

        update_query = f"""
            UPDATE payment_session
            SET {', '.join(fields)}
            WHERE user_id = %s AND session_id = %s AND id = %s
        """
        Database.execute_query(update_query, tuple(values), fetch=False)

        # Build new data snapshot by merging old record with updated fields
        new_snapshot = {**old_record[0]}
        if 'amount'      in data and data['amount']      is not None: new_snapshot['amount']      = data['amount']
        if 'description' in data and data['description'] is not None: new_snapshot['description'] = data['description']
        if 'status'      in data and data['status']      is not None: new_snapshot['status']      = data['status']
        new_data = json.dumps(new_snapshot, default=str)

        # Insert into audit table
        audit_query = """
            INSERT INTO payment_session_audit (action_type, old_data, new_data)
            VALUES (%s, %s, %s)
        """
        Database.execute_query(
            audit_query,
            ('UPDATE', old_data, new_data),
            fetch=False
        )

        return jsonify({"Message": "Payment updated successfully"}), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

# INVOICE endpointS
@payment_bp.route('/get_all_invoice/<int:account_id>',methods=['GET'])
def get_all_invoice(account_id):
	try:
		query = """
			SELECT i.*, u.full_name as username
			FROM invoice i
			JOIN user u ON i.user_id = u.id
			WHERE i.account_id = %s 
			  AND i.enabled = 1
		"""
		values =(account_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({
				"Message":"There is no invoice with this account_id "
			}),404

	except Exception as e:
		print(e)
		return jsonify({
			"Message":f"Error: {e} coming from server"
		})

@payment_bp.route('/get_invoice_by_id/<int:invoice_id>/<int:account_id>/<int:admin_user_id>', methods=['GET'])
def get_invoice_by_id(invoice_id, account_id, admin_user_id):
    try:
        query = """
            SELECT 
                i.*,
                -- Student info
                student.full_name   AS student_name,
                student.email       AS student_email,
                student.phone       AS student_phone,
                student.address     AS student_address,
                -- Academy info
                a.name             AS academy_name,
                a.file_link
                -- Admin info (logged-in user)
                admin.full_name     AS agent_name,
                admin.email         AS agent_email,
                admin.phone         AS agent_phone,
                
                -- Local info
                l.address as academy_address,
                l.name
                
            FROM invoice i
            JOIN user    student ON i.user_id    = student.id
            JOIN account a       ON i.account_id = a.id
            JOIN user    admin   ON admin.id      = %s
            JOIN local l         ON i.account_id = l.account_id
            WHERE i.id         = %s
              AND i.account_id = %s
        """
        result = Database.execute_query(
            query,
            (admin_user_id, invoice_id, account_id),
            fetch=True
        )
        if result:
            return jsonify(result[0]), 200
        else:
            return jsonify({"Message": "Invoice not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({"Message": f"Error: {e} coming from server"}), 500
