from flask import Blueprint, jsonify, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required
from util.audit import log_audit

account_section_bp = Blueprint('account_section', __name__, url_prefix='/scl')

AUDIT_TABLE = "account_section_audit"


# ─── ENDPOINT 1: Get account_section ──────────────────────────────────────────

@account_section_bp.route('/get_account_section/<int:account_id>', methods=['GET'])
def get_account_section(account_id):
    try:
        query = """
            SELECT 
                a.id,
                a.account_id,
                a.section_config_id,
                a.description,
                a.enabled,
                a.status,
                CASE 
                    WHEN a.other_section IS NOT NULL THEN a.other_section
                    ELSE s.name 
                END AS section_name
            FROM account_section a
            LEFT JOIN section_config s ON s.id = a.section_config_id
            WHERE a.account_id = %s AND a.enabled = 1
        """
        result = Database.execute_query(query, (account_id,), fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no account_section with this account_id"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 2: Create account_section ───────────────────────────────────────

@account_section_bp.route('/create_account_section/<int:account_id>', methods=['POST'])
def create_account_section(account_id):
    try:
        data        = request.get_json()
        section_id  = data.get('sectionId')
        description = data.get('description') or None
        other       = data.get('otherSection') or None

        if not section_id:
            return jsonify({"Message": "sectionId is required"}), 400

        query = """
            INSERT INTO account_section
            (account_id, section_config_id, status, description, other_section, enabled, created_at, timestamp)
            VALUES (%s, %s, 1, %s, %s, 1, NOW(), NOW())
        """
        result = Database.execute_query(query, (account_id, section_id, description, other), fetch=False)

        if result:
            # ✅ Use the lastrowid returned directly from execute_query
            inserted_id = result  # or result.lastrowid depending on what your Database class returns

            new_record = Database.execute_query(
                "SELECT * FROM account_section WHERE id = %s",
                (inserted_id,),
                fetch=True
            )
            new_rec = new_record[0] if new_record else None
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="INSERT",
                record_id=inserted_id,
                old_data=None,
                new_data=new_rec
            )
            return jsonify({"Message": "account_section created successfully"}), 200
        else:
            return jsonify({"Message": "account_section failed to create"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 3: Delete account_section (soft delete) ─────────────────────────

@account_section_bp.route('/delete_account_section/<int:account_section_id>', methods=['POST'])
def delete_account_section(account_section_id):
    try:
        old_record = Database.execute_query(
            "SELECT * FROM account_section WHERE id = %s",
            (account_section_id,),
            fetch=True
        )

        query = """
            UPDATE account_section
            SET enabled = 0
            WHERE id = %s
        """
        result = Database.execute_query(query, (account_section_id,), fetch=False)

        if result:
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="DELETE",
                record_id=account_section_id,
                old_data=old_record[0] if old_record else None,
                new_data=None
            )
            return jsonify({"Message": "account section deleted with success"}), 200
        else:
            return jsonify({"Message": "There is no account_section with this id"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 4: Update account_section ───────────────────────────────────────

@account_section_bp.route('/update_account_section/<int:account_section_id>', methods=['POST'])
def update_account_section(account_section_id):
    try:
        data        = request.get_json()
        section_id  = data.get('sectionId')
        status      = data.get('status')
        other       = data.get('other') or None
        description = data.get('description') or None

        if not section_id or status is None:
            return jsonify({"Message": "sectionId and status are required"}), 400

        old_record = Database.execute_query(
            "SELECT * FROM account_section WHERE id = %s AND enabled = 1",
            (account_section_id,),
            fetch=True
        )

        if not old_record:
            return jsonify({"Message": "account_section not found"}), 404

        query = """
            UPDATE account_section 
            SET section_config_id = %s,
                status            = %s,
                description       = %s,
                other_section     = %s,
                enabled           = 1,
                updated_at        = NOW()
                
            WHERE id = %s
        """
        result = Database.execute_query(query, (section_id, status, description, other, account_section_id), fetch=False)

        if result:
            new_record = Database.execute_query(
                "SELECT * FROM account_section WHERE id = %s",
                (account_section_id,),
                fetch=True
            )
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="UPDATE",
                record_id=account_section_id,
                old_data=old_record[0],
                new_data=new_record[0] if new_record else None
            )
            return jsonify({"Message": "account_section updated successfully"}), 200
        else:
            return jsonify({"Message": "Error in updating account_section"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 5: View account_section ─────────────────────────────────────────

@account_section_bp.route('/view_account_section/<int:account_section_id>', methods=['GET'])
def view_account_section(account_section_id):
    try:
        query = """
            SELECT *
            FROM account_section
            WHERE id = %s AND enabled = 1
        """
        result = Database.execute_query(query, (account_section_id,), fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no account_section with this id"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 6: Get section_config ───────────────────────────────────────────

@account_section_bp.route('/get_section_config', methods=['GET'])
def get_section_config():
    try:
        query = """
            SELECT *
            FROM section_config
            WHERE enabled = 1
        """
        result = Database.execute_query(query, fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no section_config"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500