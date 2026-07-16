from flask import Blueprint, jsonify, request
from flask import send_file
import sys
import os
import json
from datetime import datetime, timedelta
import bcrypt
import mysql.connector
from flask import Blueprint, request,jsonify


# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required
from util.audit import log_audit
# ========================================
# TAG ENDPOINTS
# ========================================


# Create blueprint
tag_bp = Blueprint('tag', __name__, url_prefix='/scl')

def check_exist_tag(tag_id):
	try:
		query = """
			SELECT count(*) AS nbr
			FROM tag_config 
			WHERE id = %s AND enabled = 1
		"""
		result = Database.execute_query(query,(tag_id,),fetch=True)
		return result[0]['nbr']>0
	except Exception as e:
		return False


@tag_bp.route('/get_all_tag',methods=['GET'])
def get_all_tag():
	try:
		query = """
			SELECT *
			FROM tag_config WHERE enabled = 1
		"""
		result = Database.execute_query(query,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({
				"Message":"There is no tag_config"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@tag_bp.route('/get_account_tag/<int:account_id>',methods=['GET'])
def get_account_tag(account_id):
	try:
		query = """
			SELECT
				at.id,
				at.status,
				at.description,
				at.public,
				CASE
					WHEN at.tag_config_id = 1 THEN at.other_tag
					ELSE tc.title
				END AS tag_name
			FROM account_tag at
			LEFT JOIN tag_config tc ON tc.id = at.tag_config_id
			WHERE at.account_id = %s AND at.enabled = 1
		"""
		result=Database.execute_query(query,(account_id,),fetch=True)
		if result:
			return jsonify(
				result
			),200
		else:
			return jsonify({
				"Message":"There is no account_config"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@tag_bp.route('/delete_account_tag/<int:account_tag_id>',methods=['POST'])
def delete_account_tag(account_tag_id):
	try:
		old_record = Database.execute_query(
			"SELECT * FROM account_tag WHERE id = %s",
			(account_tag_id,),
			fetch=True
		)

		query = """
			UPDATE account_tag
			set enabled = 0
			WHERE id =%s
		"""
		result = Database.execute_query(query,(account_tag_id,),fetch=False)
		if result:
			log_audit(
				table_name="account_tag_audit",
				action_type="DELETE",
				old_data=old_record[0] if old_record else None,
				new_data=None
			)
			return jsonify({
				"Message":"account_tag Delete with success"
			}),200
		else:
			return jsonify({
				"Message":"Error in deleting account_tag"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@tag_bp.route('/view_account_tag/<int:account_tag_id>',methods=['GET'])
def view_account_tag(account_tag_id):
	try:
		query = """
			SELECT *
			FROM account_tag 
			WHERE enabled = 1 AND id = %s
		"""
		result = Database.execute_query(query,(account_tag_id,),fetch=True)
		if result:
			return jsonify(
				result
			),200
		else:
			return jsonify({
				"Message":"There is no data for this id"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error {e} coming from server"
		}),500

@tag_bp.route('/edit_account_tag/<int:account_tag_id>', methods=['POST'])
def update_account_tag(account_tag_id):
    try:
        data = request.get_json()

        # ✅ Fetch old record BEFORE updating for audit
        old_record = Database.execute_query(
            "SELECT * FROM account_tag WHERE id = %s AND enabled = 1",
            (account_tag_id,),
            fetch=True
        )

        if not old_record:
            return jsonify({"Message": "Account tag not found"}), 404

        tag_config_id = data.get('tag_config_id')
        other_tag     = data.get('other_tag') or None
        status        = data.get('status')
        public        = data.get('public')
        description   = data.get('description') or None

        update_query = """
            UPDATE account_tag
            SET tag_config_id = %s,
                other_tag     = %s,
                status        = %s,
                public        = %s,
                description   = %s,
                updated_at    = NOW()
                
            WHERE id = %s
              AND enabled = 1
        """
        response = Database.execute_query(update_query, (
            tag_config_id,
            other_tag,
            status,
            public,
            description,
            account_tag_id
        ), fetch=False)

        if response:
            # ✅ Fetch updated record AFTER updating for audit
            new_record = Database.execute_query(
                "SELECT * FROM account_tag WHERE id = %s",
                (account_tag_id,),
                fetch=True
            )
            log_audit(
                table_name="account_tag_audit",
                action_type="UPDATE",

                old_data=old_record[0],
                new_data=new_record[0] if new_record else None
            )
            return jsonify({"Message": "Account tag updated with success"}), 200
        else:
            return jsonify({"Message": "Account tag update failed"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500

@tag_bp.route('/create_account_tag/<int:account_id>', methods=['POST'])
def create_account_tag(account_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"Message": "There is no data to insert it"}), 400

        tag_id      = data.get('tagId')
        description = data.get('description') or None
        other_tag   = data.get('otherTag') or None
        public      = data.get('public')
        if not check_exist_tag(tag_id):
            return jsonify({"Message": "Error in tag_id"}), 404

        query = """
            INSERT INTO account_tag (
                account_id,
                tag_config_id,
                status,
                description,
                other_tag,
                public,
                enabled,
                created_at,
                timestamp
            ) VALUES (
                %s, %s, 1, %s, %s, %s, 1, NOW(), NOW()
            )
        """
        result = Database.execute_query(query, (account_id, tag_id, description, other_tag, public), fetch=False)

        if result:
            # ✅ result is the inserted ID returned by execute_query (lastrowid)
            inserted_id = result

            new_record = Database.execute_query(
                "SELECT * FROM account_tag WHERE id = %s",
                (inserted_id,),
                fetch=True
            )
            new_rec = new_record[0] if new_record else None

            log_audit(
                table_name="account_tag_audit",
                action_type="INSERT",
                old_data=None,
                new_data=new_rec
            )
            return jsonify({"Message": "account_tag created with success"}), 200
        else:
            return jsonify({"Message": "account_tag creation failed"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ================================= COMPLETION TAG =================================
@tag_bp.route('/get_all_completion_tag/<int:account_id>',methods=['GET'])
def get_completion_tag(account_id):
	try:
		query = """
			SELECT
			 id,
			 name,
			 description,
			 status,
			 created_at
			FROM completion_tag_account 
			WHERE enabled = 1 AND account_id = %s
		"""
		values =(account_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify(
				result
			),200
		else:
			return jsonify({
				"Message":f"There is no data for this account_id"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500



AUDIT_TABLE = "completion_tag_account_audit"


# ─── ENDPOINT 1: Create completion_tag ────────────────────────────────────────

@tag_bp.route('/create_completion_tag/<int:account_id>', methods=['POST'])
def create_completion_tag(account_id):
    try:
        data        = request.get_json()
        name        = data.get('name')
        img_url     = data.get('img_url') or None
        description = data.get('description') or None

        query = """
            INSERT INTO completion_tag_account
            (account_id, name, description, status, img_link, enabled, created_at)
            VALUES (%s, %s, %s, 1, %s, 1, NOW())
        """
        values = (account_id, name, description, img_url)
        result = Database.execute_query(query, values, fetch=False)

        if result:
            inserted_id = result

            new_record = Database.execute_query(
                "SELECT * FROM completion_tag_account WHERE id = %s",
                (inserted_id,),
                fetch=True
            )
            new_rec = new_record[0] if new_record else None
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="INSERT",
                old_data=None,
                new_data=new_rec  # ✅ id is already inside this dict
            )
            return jsonify({"Message": "Success in creating completion_tag"}), 200
        else:
            return jsonify({"Message": "Error in creating completion_tag"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 2: View completion_tag ──────────────────────────────────────────

@tag_bp.route('/view_completion_tag/<int:completionTagId>', methods=['GET'])
def view_completion_tag(completionTagId):
    try:
        query = """
            SELECT 
                id,
                account_id,
                name,
                description,
                status
            FROM completion_tag_account
            WHERE enabled = 1 AND id = %s
        """
        result = Database.execute_query(query, (completionTagId,), fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no data for this id"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 3: Update completion_tag ────────────────────────────────────────

@tag_bp.route('/update_completion_tag/<int:completionTagId>', methods=['POST'])
def update_completion_tag(completionTagId):
    try:
        data = request.get_json()

        # Fetch old record before updating
        old_record = Database.execute_query(
            "SELECT * FROM completion_tag_account WHERE id = %s AND enabled = 1",
            (completionTagId,),
            fetch=True
        )

        if not old_record:
            return jsonify({"Message": "completion_tag not found"}), 404

        # Map request fields → DB columns (only include what the client can update)
        allowed_fields = {
            "name":        "name",
            "description": "description",
            "img_url":     "img_link",
            "status":      "status",
            "enabled":     "enabled",
        }

        fields_to_update = {}
        for request_key, db_column in allowed_fields.items():
            if request_key in data:
                fields_to_update[db_column] = data[request_key]

        if not fields_to_update:
            return jsonify({"Message": "No fields to update"}), 400

        # Build dynamic SET clause
        set_clause = ", ".join(f"{col} = %s" for col in fields_to_update.keys())
        values     = list(fields_to_update.values())
        values.append(completionTagId)

        query = f"""
            UPDATE completion_tag_account
            SET {set_clause}, updated_at = NOW()
            WHERE id = %s
        """
        result = Database.execute_query(query, tuple(values), fetch=False)

        if result:
            new_record = Database.execute_query(
                "SELECT * FROM completion_tag_account WHERE id = %s",
                (completionTagId,),
                fetch=True
            )
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="UPDATE",
                old_data=old_record[0],  # ✅ id is already inside this dict
                new_data=new_record[0] if new_record else None
            )

            return jsonify({"Message": "Success in updating completion_tag"}), 200
        else:
            return jsonify({"Message": "Error in updating completion_tag"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 4: Delete completion_tag (soft delete) ──────────────────────────

@tag_bp.route('/delete_completion_tag/<int:completionTagId>', methods=['POST'])
def delete_completion_tag(completionTagId):
    try:
        old_record = Database.execute_query(
            "SELECT * FROM completion_tag_account WHERE id = %s",
            (completionTagId,),
            fetch=True
        )

        query = """
            UPDATE completion_tag_account
            SET enabled = 0
            WHERE id = %s
        """
        result = Database.execute_query(query, (completionTagId,), fetch=False)

        if result:
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="DELETE",
                old_data=old_record[0],  # ✅ id is already inside this dict
                new_data=None
            )
            return jsonify({"Message": "completion_tag deleted with success"}), 200
        else:
            return jsonify({"Message": "Error in deleting completion_tag"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500