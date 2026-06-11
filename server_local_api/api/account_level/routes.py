from flask import Blueprint, jsonify, request
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

account_level_bp = Blueprint('account_level', __name__, url_prefix='/scl')


from datetime import datetime, date
from decimal import Decimal

def serialize_for_audit(obj):
    """Custom JSON serializer for types not serializable by default."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def log_audit(action_type, old_data=None, new_data=None):
    """
    Insert a record into account_level_audit table.

    Args:
        action_type: 'INSERT', 'UPDATE', or 'DELETE'
        old_data:    dict of the record BEFORE the change (None for INSERT)
        new_data:    dict of the record AFTER the change  (None for DELETE)
    """
    try:
        audit_query = """
            INSERT INTO account_level_audit (action_type, old_data, new_data)
            VALUES (%s, %s, %s)
        """
        Database.execute_query(audit_query, (
            action_type,
            json.dumps(old_data, default=serialize_for_audit) if old_data else None,
            json.dumps(new_data, default=serialize_for_audit) if new_data else None
        ), fetch=False)
    except Exception as e:
        print(f"⚠️  Audit log failed: {e}")


# ─── ENDPOINT 1: Get account levels ───────────────────────────────────────────

@account_level_bp.route('/get_account_level/<int:account_id>', methods=['GET'])
def get_account_level(account_id):
    try:
        query = """
            SELECT DISTINCT
                a.*,
                COALESCE(a.other_level, lc.name) AS level_name
            FROM account_level a
            LEFT JOIN level_config lc ON a.level_config_id = lc.id
            WHERE a.account_id = %s
              AND a.enabled = 1
        """
        result = Database.execute_query(query, (account_id,), fetch=True)
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no level for this account"}), 404
    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 2: Create account_level ─────────────────────────────────────────

@account_level_bp.route('/create_account_level/<int:account_id>', methods=['POST'])
def create_account_level(account_id):
    try:
        data = request.get_json()

        insert_query = """
            INSERT INTO account_level (account_id, level_config_id, description, enabled, created_at, timestamp, slc_edit)
            VALUES (%s, %s, %s, 1, NOW(), NOW(), 1)
        """
        values = (
            data.get('account_id'),
            data.get('level_config_id'),
            data.get('description') or None
        )
        response = Database.execute_query(insert_query, values, fetch=False)

        if response:
            # ✅ Fetch the newly created record for audit
            new_record = Database.execute_query(
                "SELECT * FROM account_level WHERE id = %s",
                (response,),
                fetch=True
            )

            log_audit(
                action_type="INSERT",
                old_data=None,
                new_data=new_record[0] if new_record else data
            )
            return jsonify({"Message": "Account_level created with success"}), 200
        else:
            return jsonify({"Message": "Error in creating account_level"}), 400

    except Exception as e:
        print(e)
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 3: Delete account_level (soft delete) ───────────────────────────

@account_level_bp.route('/delete_account_level/<int:account_id>/<int:id_account_level>', methods=['POST'])
def delete_account_level(account_id, id_account_level):
    try:
        # ✅ Fetch old record BEFORE deleting for audit
        old_record = Database.execute_query(
            "SELECT * FROM account_level WHERE account_id = %s AND id = %s",
            (account_id, id_account_level),
            fetch=True
        )

        query = """
            UPDATE account_level
            SET enabled = 0
            WHERE account_id = %s AND id = %s
        """
        response = Database.execute_query(query, (account_id, id_account_level), fetch=False)

        if response:
            log_audit(
                action_type="DELETE",
                old_data=old_record[0] if old_record else None,
                new_data=None
            )
            return jsonify({"Message": "account_level deleted with success"}), 200
        else:
            return jsonify({"Message": "Error in deleting account_level"}), 400

    except Exception as e:

        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 4: View account_level ───────────────────────────────────────────

@account_level_bp.route('/view_account_level/<int:account_level_id>')
def view_account_level(account_level_id):
    try:
        query = """
            SELECT * FROM account_level
            WHERE id = %s AND enabled = 1
        """
        response = Database.execute_query(query, (account_level_id,), fetch=True)
        if response:
            return jsonify(response), 200
        else:
            return jsonify({"Message": "There is no account_level with this id"}), 404
    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from backend"}), 500


# ─── ENDPOINT 5: Edit account_level ───────────────────────────────────────────

@account_level_bp.route('/edit_account_level/<int:account_level_id>', methods=['POST'])
def update_account_level(account_level_id):
    try:
        data = request.get_json()

        # ✅ Fetch old record BEFORE updating for audit
        old_record = Database.execute_query(
            "SELECT * FROM account_level WHERE id = %s AND enabled = 1",
            (account_level_id,),
            fetch=True
        )

        if not old_record:
            return jsonify({"Message": "Account level not found"}), 404

        level_config_id = data.get('level_config_id')
        status = data.get('status')
        description = data.get('description') or None
        other_level = data.get('other_level') or None  # ✅ add this

        update_query = """
            UPDATE account_level
            SET level_config_id = %s,
                status = %s,
                description = %s,
                other_level = %s,        -- ✅ add this
                updated_at = NOW(),
                slc_edit = 1
            WHERE id = %s
              AND enabled = 1
        """
        response = Database.execute_query(
            update_query,
            (level_config_id, status, description, other_level, account_level_id),  # ✅ add other_level
            fetch=False
        )

        if response:
            # ✅ Fetch updated record AFTER updating for audit
            new_record = Database.execute_query(
                "SELECT * FROM account_level WHERE id = %s",
                (account_level_id,),
                fetch=True
            )
            log_audit(
                action_type="UPDATE",
                old_data=old_record[0],
                new_data=new_record[0] if new_record else None
            )
            return jsonify({"Message": "Account level updated with success"}), 200
        else:
            return jsonify({"Message": "Account level update failed"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 6: Get all levels ───────────────────────────────────────────────

@account_level_bp.route('/get_all_level', methods=['GET'])
def get_all_level():
    try:
        query = "SELECT * FROM level_config WHERE enabled = 1"
        result = Database.execute_query(query, fetch=True)
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "There is no level"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {e} coming from server"}), 500