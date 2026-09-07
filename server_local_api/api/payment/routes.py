from flask import Blueprint, request, jsonify
import os
import sys
import json
from pathlib import Path
import shutil

from config import Config
from core.database import Database
from core.middleware import token_required
from core.checks import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


#create payment blueprint
payment_bp = Blueprint('payment', __name__ , url_prefix='/scl')

@payment_bp.route('/get_payment_session/<int:session_id>', methods=['GET'])
def get_payment_session(session_id):
    try:
        query = """
            SELECT count(*) AS nbr 
            FROM session WHERE id = %s AND enabled = 1
        """
        values = (session_id,)
        result = Database.execute_query(query, values, fetch=True)
        if result[0]['nbr'] == 0:
            return jsonify({
                "Message": "session Not found "
            }), 404
        else:
            query = """
                SELECT 
                    u.id AS user_id,
                    u.full_name AS full_name,
                    u.uuid AS uuid,
                    COUNT(p.id) AS paymentCount,
                    MAX(p.date_payment) AS date_payment,
                    pLatest.id AS id,
                    pLatest.price AS price,
                    pLatest.status AS status,
                    pLatest.session_id AS session_id,
                    COALESCE(vu.name, u.full_name) AS displayName
                FROM payment_session p
                JOIN user u ON p.user_id = u.id
                JOIN session s ON p.session_id = s.id
                LEFT JOIN virtual_user vu ON vu.id = (
                    SELECT MAX(vu2.id)
                    FROM virtual_user vu2
                    WHERE vu2.user_id = u.id
                      AND vu2.account_id = s.account_id
                      AND vu2.enabled = 1
                )
                LEFT JOIN payment_session pLatest ON pLatest.id = (
                    SELECT MAX(p2.id)
                    FROM payment_session p2
                    WHERE p2.user_id = p.user_id
                      AND p2.session_id = %s
                      AND p2.enabled = 1
                )
                WHERE p.session_id = %s
                  AND p.enabled = 1
                  AND s.enabled = 1
                GROUP BY u.id, u.full_name, u.uuid, vu.name, pLatest.id, pLatest.price, pLatest.status, pLatest.session_id
                ORDER BY u.full_name ASC
            """
            values = (session_id, session_id)
            result = Database.execute_query(query, values, fetch=True)

            return jsonify({
                "Message": "Success",
                "Data": result
            }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from the server"
        }), 500

@payment_bp.route('/get_payment_session_user/<int:session_id>/<int:user_id>', methods=['GET'])
def get_payment_session_user(session_id,user_id):
	try:
		query="""
			SELECT p.id, p.date_payment, p.description, p.status, p.amount, p.type_date,p.price,
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

@payment_bp.route('/get_payment_calander_user/<int:calander_id>/<int:user_id>', methods=['GET'])
def get_payment_calender_user(calander_id,user_id):
	try:
		query = """
			SELECT session_id 
			FROM relation_calander_group_session
			WHERE id = %s AND
			enabled = 1
		"""
		result = Database.execute_query(query,(calander_id,), fetch=True)
		if not result:
			return jsonify({
				"Message": f"There is no calander with this id"
			}),400

		session_id = result[0]['session_id']
		print("\n \n \n session_id: ", session_id)
		query = """
					SELECT p.id, p.date_payment, p.description, p.status, p.amount, p.type_date,
					u.full_name as username,s.name
					FROM payment_session p,user u, session s
					WHERE session_id = %s AND user_id = %s AND u.id = p.user_id AND s.id = p.session_id AND u.enabled = 1 AND s.enabled = 1 AND p.enabled = 1
				"""
		values = (session_id, user_id)
		result = Database.execute_query(query, values, fetch=True)
		if result:
			return jsonify(result), 200
		else:
			return jsonify({"Message": "There is no payment session with this id"}), 404

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from server"
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

EXCLUDED_AUDIT_FIELDS = {'uuid', 'updated_at', 'timestamp', 'created_at', 'enabled', 'type', 'created_by'}
def filter_audit_fields(record):
	return {k: v for k, v in record.items() if k not in EXCLUDED_AUDIT_FIELDS}

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

		# Fetch old data BEFORE updating (needed to know current amount/price)
		old_record_query = """
            SELECT * FROM payment_session
            WHERE user_id = %s AND session_id = %s AND id = %s
        """
		old_record = Database.execute_query(old_record_query, (user_id, session_id, payment_id), fetch=True)

		# Extra fields sent by the frontend, used to compute the status automatically
		forcing      = data.get('forcing')
		change_price = data.get('change_price')
		new_price    = data.get('new_price')
		amount       = data.get('amount')

		# Keep the RAW amount exactly as sent by the frontend, for audit purposes.
		# (amount gets overridden below when remaining_payment is used, but the
		# audit should show null if the user never typed an amount directly.)
		raw_amount = amount

		# --- Remaining payment handling ---
		remaining_payment = data.get('remaining_payment')
		amount_remaining  = data.get('amount_remaining')

		is_remaining_payment = remaining_payment in (1, '1', True)
		has_amount_remaining = amount_remaining is not None and str(amount_remaining).strip() != ''

		if is_remaining_payment and has_amount_remaining:
			try:
				old_amount = float(old_record[0].get('amount') or 0)
				amount_remaining_val = float(amount_remaining)
				amount = old_amount + amount_remaining_val  # overrides amount used for the DB update
			except (TypeError, ValueError):
				pass
		# --- END remaining payment handling ---

		# Current session price, from the existing record
		current_price = old_record[0].get('price')

		is_forcing        = forcing in (1, '1', True)
		has_change_price  = change_price in (1, '1', True)
		has_new_price     = new_price is not None and str(new_price).strip() != ''

		computed_status = None

		if amount is not None and current_price is not None:
			try:
				amount_val = float(amount)
				price_val  = float(current_price)
			except (TypeError, ValueError):
				amount_val = None
				price_val  = None

			if amount_val is not None and price_val is not None:

				# Case 1: amount == price, no change_price, no new_price -> Paid
				if amount_val == price_val and not has_change_price and not has_new_price:
					computed_status = 'Paid'
				# Case 2: forcing = 1, amount < price, no new_price -> Pending
				elif is_forcing and amount_val < price_val and not has_new_price:
					computed_status = 'Pending'
				# Case 3: forcing = 1, amount < price, new_price provided -> price changes, then compare
				elif is_forcing and amount_val < price_val and has_new_price:
					try:
						new_price_val = float(new_price)
						computed_status = 'Paid' if amount_val == new_price_val else 'Pending'
					except (TypeError, ValueError):
						computed_status = 'Pending'

		# Case 4: remaining payment that still doesn't reach the price -> Pending
		if is_remaining_payment and has_amount_remaining and computed_status is None and current_price is not None:
			try:
				if float(amount) < float(current_price):
					computed_status = 'Pending'
			except (TypeError, ValueError):
				pass

		# If a status was explicitly sent (e.g. from the Status Update Modal), it takes priority
		if 'status' in data and data['status'] is not None:
			computed_status = data['status']

		# --- Build the OLD and NEW audit snapshots ---
		old_snapshot = {
			"payment_id":       payment_id,
			"user_id":          user_id,
			"session_id":       session_id,
			"amount":           old_record[0].get('amount'),
			"price":            old_record[0].get('price'),
			"new_price":        None,
			"change_price":     False,
			"accept_payment":   True,
			"amount_remaining": None,
		}

		new_snapshot = {
			"payment_id":       payment_id,
			"user_id":          user_id,
			"session_id":       session_id,
			"amount":           raw_amount,   # null unless the user actually typed an amount
			"price":            new_price if (is_forcing and has_new_price) else current_price,
			"new_price":        new_price if has_new_price else None,
			"change_price":     has_change_price,
			"accept_payment":   True,
			"amount_remaining": amount_remaining if (is_remaining_payment and has_amount_remaining) else None,
		}

		old_data = json.dumps(old_snapshot, default=str)
		new_data = json.dumps(new_snapshot, default=str)
		# --- END snapshot building ---

		# Build dynamic update query based on provided fields only
		fields = []
		values = []

		fields.append("updated_at = NOW()")
		fields.append("date_payment = NOW()")

		if amount is not None:
			fields.append("amount = %s")
			values.append(amount)

		if 'description' in data and data['description'] is not None:
			fields.append("description = %s")
			values.append(data['description'])

		if is_forcing and has_new_price:
			fields.append("price = %s")
			values.append(new_price)

		if computed_status is not None:
			fields.append("status = %s")
			values.append(computed_status)

		# Only updated_at/date_payment were added, no real fields to update
		if len(fields) == 2:
			return jsonify({"Message": "No fields to update"}), 400

		values.extend([user_id, session_id, payment_id])

		update_query = f"""
            UPDATE payment_session
            SET {', '.join(fields)}
            WHERE user_id = %s AND session_id = %s AND id = %s
        """
		Database.execute_query(update_query, tuple(values), fetch=False)

		# Insert into audit table
		audit_query = """
            INSERT INTO payment_session_audit (action_type, old_data, new_data)
            VALUES (%s, %s, %s)
        """
		Database.execute_query(
            audit_query,
            ('UPDATE_status', old_data, new_data),
            fetch=False
        )

		return jsonify({"Message": "Payment updated successfully"}), 200

	except Exception as e:
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

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

@payment_bp.route('/get_payment_calander_session/<int:calander_id>', methods=['GET'])
def get_payment_calender_session(calander_id):
    try:
        query = """
            SELECT session_id 
            FROM relation_calander_group_session
            WHERE id = %s AND
            enabled = 1
        """
        result = Database.execute_query(query, (calander_id,), fetch=True)
        if not result:
            return jsonify({
                "Message": f"There is no calander with this id"
            }), 400

        session_id = result[0]['session_id']

        query = """
            SELECT p.user_id,
                CASE 
                    WHEN SUM(p.status = 'Unpaid') > 0 THEN 'Unpaid'
                    ELSE SUBSTRING_INDEX(GROUP_CONCAT(p.status ORDER BY p.created_at DESC), ',', 1)
                END AS status
            FROM payment_session p
            WHERE p.session_id = %s
              AND p.enabled = 1
              AND p.user_id IN (
                  SELECT a.user_id
                  FROM attendance a
                  WHERE a.calander_id = %s
                    AND a.session_id = %s
              )
            GROUP BY p.user_id
        """
        values = (session_id, calander_id, session_id)
        result = Database.execute_query(query, values, fetch=True)
        print(result)
        return jsonify(result), 200

    except Exception as e:
        print(e)
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

@payment_bp.route('/change_normal_payment_amount', methods=['POST'])
def change_normal_payment():
    try:
       data      =  request.get_json()
       userId     =  data.get('userId')
       sessionId  =  data.get('sessionId')
       newAmount  =  data.get('newAmount')

       if not(userId) or not(sessionId) or not(newAmount):
          return jsonify({
             "Message": "Missing required fields"
          }),400

       if not(session_exists(sessionId)):
          return jsonify({"Message": "There is no sesssion with this Id"}),404

       if not(user_exists(userId)):
          return jsonify({"Message": "There is no user with this Id"}),404

       query_amout = """
          SELECT *
          FROM payment_session 
          WHERE session_id = %s AND user_id = %s AND enabled = 1
       """
       result = Database.execute_query(query_amout, (sessionId, userId), fetch=True)

       if not(result):
          return jsonify({"Message": "There is no payment for this user in this session"}),404

       # Fetch old data BEFORE updating (snapshot for audit)
       old_data = json.dumps(filter_audit_fields(result[0]), default=str)

       update_query = """
          UPDATE payment_session 
          SET price = %s 
          WHERE session_id = %s AND user_id = %s AND enabled = 1
       """
       Database.execute_query(update_query, (newAmount, sessionId, userId), fetch=False)

       # Build new data snapshot by merging old record with the updated field
       new_snapshot = filter_audit_fields(result[0])
       new_snapshot['price'] = newAmount
       new_data = json.dumps(new_snapshot, default=str)

       # Insert into audit table
       audit_query = """
          INSERT INTO payment_session_audit (action_type, old_data, new_data)
          VALUES (%s, %s, %s)
       """
       Database.execute_query(
          audit_query,
          ('UPDATE_Amount', old_data, new_data),
          fetch=False
       )

       return jsonify({"Message": "Amount updated Successfully"}),200

    except Exception as e:
       return jsonify({
          "Message": f"Error: {e} coming from server"
       }), 500

@payment_bp.route('/cancel_normal_payment/<int:payment_order>', methods=['POST'])
def cancel_normal_payment(payment_order):
	try:
		query_check = """
			SELECT *
			FROM payment_session 
			WHERE id = %s AND enabled = 1
		"""
		result = Database.execute_query(query_check, (payment_order,), fetch=True)
		if not (result):
			return jsonify({"Message":"There is not payment_session_order with this Id"}), 404
		status = result[0]['status']
		status_not_allower = ['Paid', 'Not Registered']
		if status in status_not_allower:
			return jsonify({"Message": "This Payment_order cannot be cancled"}), 400

		# Fetch old data BEFORE updating (snapshot for audit)
		old_data = json.dumps(filter_audit_fields(result[0]), default=str)

		update_query = """
			UPDATE payment_session
			SET status = 'Cancelled'
			WHERE id = %s AND enabled = 1
		"""

		Database.execute_query(update_query,(payment_order,),fetch=False)

		# Build new data snapshot by merging old record record with the updated field
		new_snapshot = filter_audit_fields(result[0])
		new_snapshot['status'] = 'Cancelled'
		new_data = json.dumps(new_snapshot, default = str)

		# Insert into audit table
		audit_query = """
			INSERT INTO payment_session_audit (action_type, old_data, new_data)
			VALUES(%s, %s, %s)
		"""
		Database.execute_query(audit_query,('CANCEL', old_data, new_data),fetch=False)

		return jsonify({"Message": "Success in canceling payment_order"}),200

	except Exception as e:
		return jsonify({
			"Message": f"Error coming from server"
		}),500