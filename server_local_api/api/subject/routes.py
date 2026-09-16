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
		data = request.get_json()
		print(data)

		# Subject Data
		subject_id = data.get('subjectId')
		other_subject = data.get('otherSubject')
		description = data.get('description') or None

		# SubSubject data — list of {name, sectionId, levelId}
		sub_subjects = data.get('subSubject') or []

		if not subject_id:
			return jsonify({"Message": "Missing subject_id"}), 400

		query_test = """
            SELECT name as Name
            FROM subject_config 
            WHERE id = %s AND enabled = 1
        """
		result = Database.execute_query(query_test, (subject_id,), fetch=True)
		Name = result[0]['Name'] if result else None
		print(Name)
		if Name and Name.strip().lower() == 'other' and other_subject == None:
			return jsonify({"Message": "Other_subject must be filled "}), 400

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

			# ── Insert every sub-subject row, tied to the new account_subject ──
			query_subsubject = """
                INSERT INTO account_sub_subject 
                    (account_id, account_section_id, account_level_id, account_subject_id, name) 
                VALUES (%s, %s, %s, %s, %s)
            """

			inserted_sub_records = []

			for sub in sub_subjects:
				sub_name = sub.get('name')
				sub_section_id = sub.get('sectionId')
				sub_level_id = sub.get('levelId')

				if not sub_name:
					continue  # skip incomplete entries

				sub_values = (account_id, sub_section_id, sub_level_id, inserted_id, sub_name)

				sub_inserted_id = Database.execute_query(query_subsubject, sub_values, fetch=False)

				if sub_inserted_id:
					new_sub_record = Database.execute_query(
						"SELECT * FROM account_sub_subject WHERE id = %s",
						(sub_inserted_id,),
						fetch=True
					)
					new_sub_rec = new_sub_record[0] if new_sub_record else None

					if new_sub_rec:
						inserted_sub_records.append(new_sub_rec)

					# audit log for the sub_subject table itself
					log_audit(
						table_name="account_sub_subject_audit",
						action_type="INSERT",
						old_data=None,
						new_data=new_sub_rec
					)

			# ── Audit log for account_subject — now AFTER sub_subject inserts,
			#    and includes the sub_subject rows in its new_data ─────────────
			audit_new_data = dict(new_rec) if new_rec else {}
			audit_new_data["sub_subjects"] = inserted_sub_records

			log_audit(
				table_name=AUDIT_TABLE,
				action_type="INSERT",
				old_data=None,
				new_data=audit_new_data
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
		data = request.get_json()
		print(data)
		subject_id = data.get('subjectId')
		status = data.get('status') or 1
		description = data.get('description') or None
		other_subject = data.get('otherSubject') or None

		# SubSubject data
		sub_subjects_add = data.get('subSubjects') or []  # list of {account_section_id, account_level_id, name}
		sub_subjects_delete = data.get('subSubjects_delete') or []  # list of ids

		if not subject_id:
			return jsonify({"Message": "Missing subject_id"}), 400

		old_record = Database.execute_query(
			"SELECT * FROM account_subject WHERE id = %s AND enabled = 1",
			(account_subject_id,),
			fetch=True
		)

		if not old_record:
			return jsonify({"Message": "account_subject not found"}), 404

		account_id = old_record[0]['account_id']

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

		if not result:
			return jsonify({"Message": "Error updating account_subject"}), 400

		# ── Insert new sub-subjects ──────────────────────────────────────
		query_subsubject = """
            INSERT INTO account_sub_subject 
                (account_id, account_section_id, account_level_id, account_subject_id, name, enabled) 
            VALUES (%s, %s, %s, %s, %s, 1)
        """

		inserted_sub_records = []

		for sub in sub_subjects_add:
			sub_name = sub.get('name')
			sub_section_id = sub.get('account_section_id')
			sub_level_id = sub.get('account_level_id')

			if not sub_name:
				continue  # skip incomplete entries

			sub_values = (account_id, sub_section_id, sub_level_id, account_subject_id, sub_name)

			sub_inserted_id = Database.execute_query(query_subsubject, sub_values, fetch=False)

			if sub_inserted_id:
				new_sub_record = Database.execute_query(
					"SELECT * FROM account_sub_subject WHERE id = %s",
					(sub_inserted_id,),
					fetch=True
				)
				new_sub_rec = new_sub_record[0] if new_sub_record else None

				if new_sub_rec:
					inserted_sub_records.append(new_sub_rec)

				log_audit(
					table_name="account_sub_subject_audit",
					action_type="INSERT",
					old_data=None,
					new_data=new_sub_rec
				)

		# ── Soft-delete removed sub-subjects (enabled = 0) ───────────────
		deleted_sub_records = []

		for sub_id in sub_subjects_delete:
			old_sub_record = Database.execute_query(
				"SELECT * FROM account_sub_subject WHERE id = %s AND enabled = 1",
				(sub_id,),
				fetch=True
			)
			old_sub_rec = old_sub_record[0] if old_sub_record else None

			if not old_sub_rec:
				continue  # already deleted / doesn't exist, skip

			Database.execute_query(
				"UPDATE account_sub_subject SET enabled = 0 WHERE id = %s",
				(sub_id,),
				fetch=False
			)

			new_sub_record = Database.execute_query(
				"SELECT * FROM account_sub_subject WHERE id = %s",
				(sub_id,),
				fetch=True
			)
			new_sub_rec = new_sub_record[0] if new_sub_record else None
			deleted_sub_records.append(new_sub_rec)

			log_audit(
				table_name="account_sub_subject_audit",
				action_type="UPDATE",
				old_data=old_sub_rec,
				new_data=new_sub_rec
			)

		# ── Audit log for account_subject itself ─────────────────────────
		new_record = Database.execute_query(
			"SELECT * FROM account_subject WHERE id = %s",
			(account_subject_id,),
			fetch=True
		)

		audit_new_data = dict(new_record[0]) if new_record else {}
		audit_new_data["sub_subjects_added"] = inserted_sub_records
		audit_new_data["sub_subjects_deleted"] = deleted_sub_records

		log_audit(
			table_name=AUDIT_TABLE,
			action_type="UPDATE",
			old_data=old_record[0],
			new_data=audit_new_data
		)

		return jsonify({"Message": "account_subject updated successfully"}), 200

	except Exception as e:
		return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ─── ENDPOINT 7: Delete account_subject (soft delete) ─────────────────────────
@subject_bp.route('/delete_account_subject/<int:account_subject_id>', methods=['POST'])
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


# ─── ENDPOINT 8: Fetch account_sub_subject ─────────────────────────
@subject_bp.route('/get_account_sub_subject/<int:account_subject_id>', methods=['GET'])
def get_account_sub_subject(account_subject_id):
	try:
		query_test = """
            SELECT * FROM account_subject WHERE id = %s AND enabled = 1
        """
		result = Database.execute_query(query_test, (account_subject_id,), fetch=True)
		if not result:
			return jsonify({"Message": "Error There is no subject_config with this id"}), 404
		query_data = """
            SELECT id, account_id, account_section_id, account_level_id, account_subject_id, name 
            FROM account_sub_subject 
            WHERE account_subject_id = %s  AND enabled = 1
        """
		data = Database.execute_query(query_data, (account_subject_id,), fetch=True)
		if data:
			return jsonify(data), 200
		else:
			return jsonify({"Message": "Error There is no subject_config with this id"}), 404


	except Exception as e:
		return jsonify({"Message": f"Error: {e} coming from server"}), 500


@subject_bp.route('/get_sub_subject/<int:section_id>/<int:level_id>', methods=['GET'])
def get_sub_subject(section_id, level_id):
	try:

		query_fetch = """
			SELECT id ,account_subject_id, name
			FROM account_sub_subject 
			WHERE account_section_id = %s AND account_level_id = %s 
			AND enabled = 1
		"""
		values = (section_id, level_id)
		result = Database.execute_query(query_fetch, values, fetch=True)
		if result:
			return jsonify(result), 200
		else:
			return jsonify({"Message": "Error There is no subject_config with this id"}), 404
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}),500
