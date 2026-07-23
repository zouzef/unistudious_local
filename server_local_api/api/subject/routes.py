from flask import Blueprint, jsonify, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required
from util.audit import log_audit


subject_bp = Blueprint('subjects', __name__, url_prefix='/scl')

AUDIT_TABLE = "account_subject_audit"


# ─── ENDPOINT 1: Get all sub_subject ──────────────────────────────────────────

@subject_bp.route('/get_sub_subjects', methods=['GET'])
def get_subjects():
    try:
        query = """
            SELECT 
                a.subject_config_id,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE sc.name
                END AS subject_identifier
            FROM account_subject a
            LEFT JOIN subject_config sc ON sc.id = a.subject_config_id 
            WHERE a.enabled = 1 
              AND a.status = 1
              AND sc.enabled = 1
        """
        result = Database.execute_query(query, fetch=True)
        return jsonify({
            "Message": "Success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from the server"}), 500


# ─── ENDPOINT 2: Get subject_config ───────────────────────────────────────────

@subject_bp.route('/get_subject_config', methods=['GET'])
def get_subject_config():
    try:
        query = """
            SELECT *
            FROM subject_config
            WHERE enabled = 1 AND status = 1
        """
        result = Database.execute_query(query, fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no subjects for this account"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 3: Get account_subject by account_id ────────────────────────────

@subject_bp.route('/get_account_subject/<int:account_id>', methods=['GET'])
def get_account_subject(account_id):
    try:
        query = """
            SELECT DISTINCT
                a.id,
                a.account_id,
                a.subject_config_id,
                a.description,
                a.enabled,
                a.status,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE s.name 
                END AS section_name
            FROM account_subject a
            LEFT JOIN subject_config s ON s.id = a.subject_config_id
            WHERE a.account_id = %s AND a.enabled = 1 AND s.enabled = 1 AND s.status = 1 AND a.status = 1
        """
        result = Database.execute_query(query, (account_id,), fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no account_subject for this id"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 4: View account_subject ─────────────────────────────────────────

@subject_bp.route('/view_account_subject/<int:account_subject_id>', methods=['GET'])
def view_account_subject(account_subject_id):
    try:
        query = """
            SELECT 
                a.id,
                a.account_id,
                a.subject_config_id,
                a.description,
                a.enabled,
                a.status,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE s.name 
                END AS section_name
            FROM account_subject a
            LEFT JOIN subject_config s ON s.id = a.subject_config_id
            WHERE a.id = %s AND a.enabled = 1 AND s.enabled = 1
        """
        result = Database.execute_query(query, (account_subject_id,), fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"Message": "There is no Data for this id"}), 404

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from backend"}), 500


# ─── ENDPOINT 5: Create account_subject ───────────────────────────────────────

@subject_bp.route('/create_account_subject/<int:account_id>', methods=['POST'])
def create_account_subject(account_id):
    try:
        data          = request.get_json()
        subject_id    = data.get('subjectId')
        other_subject = data.get('other_subject') or None
        description   = data.get('description') or None

        if not subject_id:
            return jsonify({"Message": "Missing subject_id"}), 400

        query = """
            INSERT INTO account_subject
                (account_id, subject_config_id, status, description, other_subject, enabled, created_at, timestamp, slc_use)
            VALUES (%s, %s, 1, %s, %s, 1, NOW(), NOW(), 1)
        """
        result = Database.execute_query(query, (account_id, subject_id, description, other_subject), fetch=False)

        if result:
            inserted_id = result

            new_record = Database.execute_query(
                "SELECT * FROM account_subject WHERE id = %s",
                (inserted_id,),
                fetch=True
            )
            new_rec = new_record[0] if new_record else None

            log_audit(
                table_name=AUDIT_TABLE,
                action_type="INSERT",

                old_data=None,
                new_data=new_rec
            )

            return jsonify({"Message": "subject_config created with success"}), 200
        else:
            return jsonify({"Message": "Error in creating subject_config"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 6: Update account_subject ───────────────────────────────────────

@subject_bp.route('/update_account_subject/<int:account_subject_id>', methods=['POST'])
def update_account_subject(account_subject_id):
    try:
        data          = request.get_json()
        subject_id    = data.get('subjectId')
        status        = data.get('status') or 1
        description   = data.get('description') or None
        other_subject = data.get('otherSubject') or None

        if not subject_id:
            return jsonify({"Message": "Missing subject_id"}), 400

        old_record = Database.execute_query(
            "SELECT * FROM account_subject WHERE id = %s AND enabled = 1",
            (account_subject_id,),
            fetch=True
        )

        if not old_record:
            return jsonify({"Message": "account_subject not found"}), 404

        query = """
            UPDATE account_subject
            SET subject_config_id = %s,
                status            = %s,
                description       = %s,
                other_subject     = %s,
                timestamp         = NOW()
            WHERE id = %s
        """
        result = Database.execute_query(
            query,
            (subject_id, status, description, other_subject, account_subject_id),
            fetch=False
        )

        if result:
            new_record = Database.execute_query(
                "SELECT * FROM account_subject WHERE id = %s",
                (account_subject_id,),
                fetch=True
            )
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="UPDATE",
                old_data=old_record[0],
                new_data=new_record[0] if new_record else None
            )
            return jsonify({"Message": "account_subject updated successfully"}), 200
        else:
            return jsonify({"Message": "Error updating account_subject"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 7: Delete account_subject (soft delete) ─────────────────────────

@subject_bp.route('/delete_account_subject/<account_subject_id>', methods=['POST'])
def delete_account_subject(account_subject_id):
    try:
        old_record = Database.execute_query(
            "SELECT * FROM account_subject WHERE id = %s",
            (account_subject_id,),
            fetch=True
        )

        query = """
            UPDATE account_subject
            SET enabled = 0
            WHERE id = %s
        """
        result = Database.execute_query(query, (account_subject_id,), fetch=False)

        if result:
            log_audit(
                table_name=AUDIT_TABLE,
                action_type="DELETE",

                old_data=old_record[0] if old_record else None,
                new_data=None
            )
            return jsonify({"Message": "Subject_config deleted with success"}), 200
        else:
            return jsonify({"Message": "Error in deleting subject_config"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500