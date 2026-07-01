from flask import Blueprint,jsonify, request
import uuid
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


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


# ========================================
# ENDPOINT 3: Update Virtual user by id
# ========================================
@Vusers_bp.route('/update-virtual-user/<int:id>', methods=['POST'])
def update_virtuel_user(id):
    try:
        # ── Fetch existing row first — needed for old_data + existence check ──
        existing = Database.execute_query(
            "SELECT * FROM virtual_user WHERE id = %s",
            (id,)
        )
        if not existing:
            return jsonify({"Message": "Virtual user not found"}), 404

        old_row = existing[0]

        data = request.get_json()

        # ── Map allowed fields: payload_key → database_column ────
        allowed_fields = {
            'name':   'name',
            'email':  'email',
            'phone':  'phone',
            'status': 'status',
        }

        # ── Build SET clause only from fields present in request ─
        set_clauses = []
        values = []
        updated_payload = {}

        for payload_key, db_column in allowed_fields.items():
            if payload_key in data:
                value = data[payload_key]

                if value == '' or value is None:
                    value = None

                set_clauses.append(f"{db_column} = %s")
                values.append(value)
                updated_payload[db_column] = value

        if not set_clauses:
            return jsonify({"Message": "No fields to update"}), 400

        set_clauses.append("slc_edit = 1")
        set_clauses.append("updated_at = NOW()")

        values.append(id)

        query = f"UPDATE virtual_user SET {', '.join(set_clauses)} WHERE id = %s"
        Database.execute_query(query, tuple(values), fetch=False)

        # ── Audit log ──────────────────────────────────────────────
        # old_data: only the fields that were actually touched, before the update
        old_data = {k: old_row.get(k) for k in updated_payload.keys()}
        old_data["id"] = id

        new_data = dict(updated_payload)
        new_data["id"] = id

        audit_query = """
            INSERT INTO virtual_user_audit (action_type, record_id, old_data, new_data, is_synced)
            VALUES (%s, %s, %s, %s, %s)
        """
        Database.execute_query(
            audit_query,
            [
                "UPDATE",
                id,
                json.dumps(old_data, default=str),
                json.dumps(new_data, default=str),
                0
            ],
            fetch=False
        )

        return jsonify({"Message": "Virtual user updated successfully"}), 200

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from update virtual user"}), 500


# ========================================
# ENDPOINT 4: Create virtual user
# ========================================
