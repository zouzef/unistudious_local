from flask import Blueprint,jsonify, request
import uuid
import os
import sys
import json
from datetime import datetime
from config import Config
from core.database import Database
from core.middleware import token_required

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))



# ========================================
# Virtual User Endpoints
# ========================================

#create blueprint
Vusers_bp = Blueprint('virtual_users', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Get virtual users by account and session
# ========================================
@Vusers_bp.route('/get-all-virtuel-user/<int:account_id>',methods=['GET'])
def get_all_virtuel_user(account_id):
	try:
		query = """
			SELECT 
				id,
				user_id,
				name,
				created_by_id,
				phone,
				email,
				data
			FROM virtual_user 
			WHERE enabled = 1 AND account_id = %s
		"""
		values = (account_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify({
				"Message":"Success",
				"data":result
			}),200
		else:
			return jsonify({
				"Message":"There is no data from this account_id",
				"Data":[]
			}),404
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from get all_virtuel_users"
		}),500


# ========================================
# ENDPOINT 2: Delete virtual user by id
# ========================================
@Vusers_bp.route('/delete-virtuel-user/<int:id>',methods=['POST'])
def delete_virtuel_user(id):
	try:
		query = """
			UPDATE virtual_user
			 set enabled = 0 , slc_edit = 1
			 where id = %s
			 
		"""
		values = (id,)
		result = Database.execute_query(query,values,fetch=False)
		return jsonify({
			"Message":"Virtuel_user deleted "
		}),200

	except Exception as e:
		return jsonify({
			"Message":f"Error : {e} coming from delete virtuel user"
		}),500


# =============================================
# ENDPOINT 3: UPDATE Virtuel User
# =============================================
@Vusers_bp.route('/update-virtual-student/<int:account_id>', methods=['POST'])
def update_virtual_student(account_id):
	try:
		data = request.get_json() if request.is_json else request.form

		user_id = data.get('userId')
		vu_id   = data.get('id')
		name    = data.get('name')
		phone   = data.get('phone')
		email   = data.get('email')
		status  = data.get('status')

		if not user_id or not vu_id:
			return jsonify({"message": "UserId and Id are required."}), 400

		user_row = Database.execute_query(
            "SELECT id FROM user WHERE id = %s AND enabled = 1", (user_id,)
        )
		if not user_row:
			return jsonify({"success": False, "message": "Student not found"}), 400

		vu_row = Database.execute_query(
            "SELECT id, name, phone, email, status, user_id, account_id FROM virtual_user WHERE user_id = %s AND account_id = %s AND enabled = 1 AND id = %s",
            (user_id, account_id, vu_id)
		)

		if not vu_row:
			# create
			insert_query = """
                INSERT INTO virtual_user (name, phone, email, status, user_id, account_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
			result = Database.execute_query(
				insert_query,
                (name, phone, email, bool(status), user_id, account_id),
                fetch=False
			)
			vu_id = result

			new_row = Database.execute_query(
                "SELECT id, name, phone, email, status, user_id, account_id FROM virtual_user WHERE id = %s",
                (vu_id,)
            )[0]

			# audit: creation (old_data null, new_data = full new row)
			Database.execute_query(
                """
                INSERT INTO virtual_user_audit (action_type, record_id, old_data, new_data)
                VALUES (%s, %s, %s, %s)
                """,
                ('create', vu_id, None, json.dumps(new_row, default=str)),
                fetch=False
            )

		else:
			old_row = vu_row[0]

			set_clauses = []
			values = []
			if name:
				set_clauses.append("name = %s"); values.append(name)
			if phone:
				set_clauses.append("phone = %s"); values.append(phone)
			if email:
				set_clauses.append("email = %s"); values.append(email)
			if status:
				set_clauses.append("status = %s"); values.append(bool(status))

			if set_clauses:
				values.append(vu_id)
				query = f"UPDATE virtual_user SET {', '.join(set_clauses)} WHERE id = %s"
				Database.execute_query(query, tuple(values), fetch=False)

				new_row = Database.execute_query(
                    "SELECT id, name, phone, email, status, user_id, account_id FROM virtual_user WHERE id = %s",
                    (vu_id,)
                )[0]

				# audit: update (old_data = row before, new_data = row after)
				Database.execute_query(
                    """
                    INSERT INTO virtual_user_audit (action_type, record_id, old_data, new_data)
                    VALUES (%s, %s, %s, %s)
                    """,
                    ('update', vu_id, json.dumps(old_row, default=str), json.dumps(new_row, default=str)),
                    fetch=False
                )

		result = Database.execute_query(
            "SELECT id, user_id, name, email, phone, status, account_id FROM virtual_user WHERE id = %s",
            (vu_id,)
        )
		vu = result[0]

		return jsonify({
            "success": True,
            "message": "Virtual student updated successfully",
            "student": {
                "id": vu['id'],
                "userId": vu['user_id'],
                "fullName": vu['name'],
                "email": vu['email'],
                "phone": vu['phone'],
                "status": "Active" if vu['status'] else "Inactive",
                "account": vu['account_id'],
                "type": "Virtual",
            }
        }), 200

	except Exception as e:
		return jsonify({"success": False, "message": "Error updating virtual student"}), 500


# =============================================
# ENDPOINT 4: CREATE VirtuelUser
# =============================================
@Vusers_bp.route('/create_virtuel_user/<int:account_id>',methods=['POST'])
def create_virtuel_user(account_id):
	try:
		data = request.form.to_dict()
		files = request.files

		full_name = data.get("fullName")
		email = data.get("email")
		phone = data.get("phone")
		status = data.get("status") or 1

		if not full_name or not email:
			return jsonify({
				"Message": "full_name, email are required"
			}), 400

		# ── Generate username (adjust pattern to match your real username generator) ──
		base_username = "".join(c for c in full_name.lower() if c.isalnum())[:20] or "user"
		suffix = "".join(random.choices(string.digits, k=4))
		generated_username = f"{base_username}{suffix}"

		virtual_email = f"{generated_username}@virtual-unistudious.com"

		# ── 1. Create the User row ────────────────────────────────────
		user_data = {
			"account_id": account_id,
			"username": generated_username,
			"email": virtual_email,
			"full_name": full_name,
			"roles": json.dumps(["ROLE_USER"]),
			"password": generated_username,  # plain text, matching current local pattern — flag if this needs hashing
			"phone": phone,
			"status": 1 if str(status) in ("1", "true", "True") else 0,
			"enabled": 1,
			"isvirtual": 1,
			"created_by": 0,  # TODO: replace with real admin user id if available
		}

		filtered_user_data = {k: v for k, v in user_data.items() if v is not None}

		columns = ", ".join(filtered_user_data.keys())
		placeholders = ", ".join(["%s"] * len(filtered_user_data))
		values = list(filtered_user_data.values())

		query = f"INSERT INTO user ({columns}) VALUES ({placeholders})"
		user_result = Database.execute_query(query, values, fetch=False)

		if not user_result:
			return jsonify({"Message": "User not created"}), 400

		# ── 2. Create the VirtualUser row, linked via user_id ─────────
		virtual_uuid = str(uuid.uuid4())

		virtual_user_data = {
			"account_id": account_id,
			"user_id": user_result,
			"created_by_id": 0,  # TODO: replace with real admin user id if available
			"name": full_name,
			"phone": phone,
			"email": email,
			"status": 1 if str(status) in ("1", "true", "True") else 0,
			"enabled": 1,
			"uuid": virtual_uuid,
		}

		filtered_virtual_data = {k: v for k, v in virtual_user_data.items() if v is not None}

		v_columns = ", ".join(filtered_virtual_data.keys())
		v_placeholders = ", ".join(["%s"] * len(filtered_virtual_data))
		v_values = list(filtered_virtual_data.values())

		virtual_query = f"INSERT INTO virtual_user ({v_columns}) VALUES ({v_placeholders})"
		virtual_result = Database.execute_query(virtual_query, v_values, fetch=False)

		if not virtual_result:
			return jsonify({"Message": "Virtual user not created"}), 400

		# ── Audit log ──────────────────────────────────────────────────
		audit_payload = dict(filtered_user_data)
		audit_payload["id"] = user_result
		audit_payload["virtual_user_id"] = virtual_result

		audit_query = """
		    INSERT INTO virtual_user_audit (action_type, record_id, old_data, new_data, is_synced)
		    VALUES (%s, %s, %s, %s, %s)
		"""
		Database.execute_query(
			audit_query,
			[
				"CREATE",
				virtual_result,  # record_id → the virtual_user's PK
				None,  # old_data → nothing before creation
				json.dumps(audit_payload),  # new_data → the created record
				0
			],
			fetch=False
		)

		return jsonify({
			"Message": "Virtual student created successfully",
			"user_id": user_result,
			"virtual_user_id": virtual_result
		}), 200

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500