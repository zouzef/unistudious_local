from flask import Blueprint, jsonify, request, current_app
import json
import sys
import os

from werkzeug.utils import secure_filename
# Add parent directories to path
from config import Config
from core.database import Database
from util.audit import log_audit
from werkzeug.utils import secure_filename
from flask import send_from_directory

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

formation_bp = Blueprint('formation', __name__, url_prefix='/scl')


# Service check formation
def check_formation(formation_id):
	try:
		query = """
					SELECT COUNT(*) AS nbr
					FROM formation 
					WHERE id=%s AND enabled = 1
				"""
		values = (formation_id,)
		result = Database.execute_query(query, values, fetch=True)

		return result[0]['nbr'] > 0

	except Exception as e:
		return False


@formation_bp.route('/get-formation-info/<int:account_id>', methods=['GET'])
def get_formation_info(account_id):
	try:
		query = """
			SELECT 
				   f.id,
				   f.name,
				   f.description,
				   f.type_session,
				   f.number_day_duration,
				   f.number_session,
				   f.img_link,
				   f.condition_of_passage,
				   f.status,
				   f.created_at,
				   acs.other_section as section,
				   al.other_level as level,
				   COUNT(s.id) AS sessions_count
			FROM formation f
			JOIN account_section acs ON acs.id = f.account_section_id
			JOIN account_level al ON al.id = f.account_level_id
			LEFT JOIN session s ON s.formation_id = f.id 
			WHERE f.account_id = %s
			  AND f.enabled = 1
			GROUP BY f.id, f.name, f.description, f.type_session, f.number_day_duration,
					f.number_session, f.condition_of_passage, f.status, f.created_at,
					acs.other_section, al.other_level
			ORDER BY f.created_at DESC
		"""
		values = (account_id,)
		result = Database.execute_query(query, values)

		if result:
			return jsonify({
				"Data": result
			}), 200
		else:
			return jsonify({
				"Message": "Error",
				"Data": []
			}), 404


	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from get_formation_info"
		}), 500


@formation_bp.route('/delete_formation/<int:formation_id>/<int:account_id>', methods=['POST'])
def delete_formation(formation_id, account_id):
	try:
		if not check_formation(formation_id):
			return jsonify({
				"Message": "There is no formation with this id"
			}), 404

		# ✅ Get old record before delete
		old_record = Database.execute_query(
			"""
			SELECT *
			FROM formation
			WHERE id = %s AND account_id = %s
			""",
			(formation_id, account_id),
			fetch=True
		)

		query = """
            UPDATE formation
            SET enabled = 0,
                updated_at = NOW()
            WHERE id = %s
              AND account_id = %s
        """

		result = Database.execute_query(
			query,
			(formation_id, account_id),
			fetch=False
		)

		if result:
			# ✅ Audit log
			log_audit(
				table_name="formation_audit",
				action_type="DELETE",
				old_data=old_record[0] if old_record else None,
				new_data=None
			)

			return jsonify({
				"Message": "Formation deleted with success"
			}), 200

		return jsonify({
			"Message": "Failed to delete formation"
		}), 400

	except Exception as e:
		print(e)
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500


@formation_bp.route('/view_formation/<int:formation_id>', methods=['GET'])
def view_formation(formation_id):
	try:
		if not (check_formation(formation_id)):
			return jsonify({
				"Message": "There is no formation with this id"
			}), 404
		query = """
		    SELECT 
				DISTINCT
				f.name,
				f.status,
				f.type_date,
				f.number_day_duration,
				f.number_session,
				f.type_session,
				f.condition_of_passage,
				f.public_resource,
				f.description
			FROM formation f
			
			WHERE f.id = %s AND f.enabled = 1
		"""
		result = Database.execute_query(query, (formation_id,), fetch=True)
		return jsonify(result), 200

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from server"
		})


@formation_bp.route('/update_formation/<int:formation_id>', methods=['POST'])
def update_formation(formation_id):
	try:
		data = request.get_json()

		# ✅ Get old record before update
		old_record = Database.execute_query(
			"""
			SELECT *
			FROM formation
			WHERE id = %s
			  AND enabled = 1
			""",
			(formation_id,),
			fetch=True
		)

		if not old_record:
			return jsonify({
				"Message": "Formation not found"
			}), 404

		# camelCase (JS payload) -> snake_case (DB column)
		field_map = {
			'name': 'name',
			'status': 'status',
			'typeDate': 'type_date',
			'otherTypeDate': 'other_type_date',
			'numberDayDuration': 'number_day_duration',
			'numberSession': 'number_session',
			'typeSession': 'type_session',
			'otherTypeSession': 'other_type_session',
			'conditionOfPassage': 'condition_of_passage',
			'conditionOfPassageFormule': 'condition_of_passage_formule',
			'conditionOfPassageFormuleByNote': 'condition_of_passage_formule_by_note',
			'conditionOfPassageFormuleByPresent': 'condition_of_passage_formule_by_present',
			'conditionOfPassageFormuleByNotePresent': 'condition_of_passage_formule_by_note_present',
			'publicResource': 'public_resource',
			'description': 'description',
			'accountSection': 'account_section_id',
			'accountLevel': 'account_level_id',
			'imgLink': 'img_link',
		}

		# Fields that are FK / nullable ints, where '' should become NULL
		nullable_fields = {
			'accountSection',
			'accountLevel',
			'otherTypeDate',
			'otherTypeSession',
			'numberDayDuration',
			'numberSession',
			'conditionOfPassageFormule',
			'conditionOfPassageFormuleByNote',
			'conditionOfPassageFormuleByPresent',
			'conditionOfPassageFormuleByNotePresent',
			'publicResource',
			'description',
			'imgLink',
		}

		fields_to_update = {}
		for k, v in data.items():
			if k not in field_map:
				continue

			if k in nullable_fields:
				if isinstance(v, str):
					v = v.strip() or None
				elif v == '':
					v = None

			if k == 'name' and isinstance(v, str):
				v = v.strip()

			fields_to_update[field_map[k]] = v

		if not fields_to_update:
			return jsonify({
				"Message": "No fields provided to update"
			}), 400

		set_clause = ", ".join(
			[f"{col} = %s" for col in fields_to_update.keys()]
		)

		values = list(fields_to_update.values())
		values.append(formation_id)

		query = f"""
            UPDATE formation
            SET {set_clause},
                updated_at = NOW()
            WHERE id = %s
        """

		result = Database.execute_query(
			query,
			values,
			fetch=False
		)

		if result:
			updated_record = Database.execute_query(
				"SELECT * FROM formation WHERE id = %s",
				(formation_id,),
				fetch=True
			)

			log_audit(
				table_name="formation_audit",
				action_type="UPDATE",
				old_data=old_record[0],
				new_data=updated_record[0] if updated_record else data
			)

			return jsonify({
				"Message": "Formation updated successfully"
			}), 200

		return jsonify({
			"Message": "Error updating formation"
		}), 400

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500


@formation_bp.route('/create_formation/<int:account_id>', methods=['POST'])
def create_formation(account_id):
	try:
		data = request.form
		files = request.files

		required_fields = [
			'name',
			'typeDate',
			'typeSession',
		]

		for field in required_fields:
			if not data.get(field):
				return jsonify({"Message": f"'{field}' is required"}), 400

		name = (data.get('name') or '').strip()
		status = 1

		account_level_id = data.get('accountLevel') or None
		account_section_id = data.get('accountSection') or None
		type_date = data.get('typeDate')
		other_type_date = (data.get('otherTypeDate') or '').strip() or None
		number_day_duration = data.get('numberDayDuration') or None
		number_session = data.get('numberSession') or None
		type_session = data.get('typeSession')
		other_type_session = (data.get('otherTypeSession') or '').strip() or None
		condition_of_passage = data.get('conditionOfPassage')
		condition_of_passage_formule = data.get('conditionOfPassageFormule') or None
		condition_of_passage_formule_by_note = (data.get('conditionOfPassageFormuleByNote') or '').strip() or None
		condition_of_passage_formule_by_present = (data.get('conditionOfPassageFormuleByPresent') or '').strip() or None
		condition_of_passage_formule_by_note_present = (data.get(
			'conditionOfPassageFormuleByNotePresent') or '').strip() or None

		public_resource = data.get('publicResource') or None
		description = (data.get('description') or '').strip() or None

		img_link = None  # unknown until after INSERT

		# ------------------ Create formation ------------------
		query = """
            INSERT INTO formation (
                account_id,
                account_level_id,
                account_section_id,
                name,
                description,
                status,
                type_date,
                other_type_date,
                type_session,
                other_type_session,
                number_day_duration,
                number_session,
                condition_of_passage,
                condition_of_passage_formule,
                condition_of_passage_formule_by_note,
                condition_of_passage_formule_by_present,
                condition_of_passage_formule_by_note_present,
                img_link,
                public_resource,
                enabled,
                created_at,
                updated_at
            ) VALUES (
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,
                1,
                NOW(),NOW()
            )
        """

		values = [
			account_id,
			account_level_id,
			account_section_id,
			name,
			description,
			status,
			type_date,
			other_type_date,
			type_session,
			other_type_session,
			number_day_duration,
			number_session,
			condition_of_passage,
			condition_of_passage_formule,
			condition_of_passage_formule_by_note,
			condition_of_passage_formule_by_present,
			condition_of_passage_formule_by_note_present,
			img_link,
			public_resource
		]

		result = Database.execute_query(query, values, fetch=False)

		if not result:
			return jsonify({"Message": "Formation not created"}), 400

		formation_id = result

		# ------------------ Save image ------------------
		image_file = files.get("formation_logoFile")

		img_link = None

		if image_file and image_file.filename:
			filename = secure_filename(image_file.filename)

			upload_folder = os.path.join(
				current_app.root_path,
				"uploads",
				"formation_img",
				f"formation_{formation_id}"
			)

			try:
				os.makedirs(upload_folder, exist_ok=True)
			except Exception as e:
				print("ERROR creating folder:", e)

			save_path = os.path.join(upload_folder, filename)

			try:
				image_file.save(save_path)

			except Exception as e:
				print("ERROR saving image:", e)

			img_link = filename

			print("8 - img_link:", img_link)

			Database.execute_query(
				"UPDATE formation SET img_link = %s, updated_at = NOW() WHERE id = %s",
				[img_link, formation_id],
				fetch=False
			)

		# ------------------ Fetch final record for audit ------------------
		new_record = Database.execute_query(
			"SELECT * FROM formation WHERE id = %s",
			[formation_id],
			fetch=True
		)

		log_audit(
			table_name="formation_audit",
			action_type="INSERT",
			old_data=None,
			new_data=new_record[0] if new_record else dict(data)
		)

		return jsonify({
			"Message": "Formation created successfully",
			"formation_id": formation_id,
			"img_link": img_link
		}), 200

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500


@formation_bp.route('/get_formation_image/<int:formation_id>', methods=['GET'])
def get_formation_image(formation_id):
	try:
		query = """
		   SELECT img_link 
		   FROM formation
		   WHERE id = %s AND enabled = 1
		"""
		result = Database.execute_query(query, (formation_id,), fetch=True)

		if not result or not result[0].get('img_link'):
			return jsonify({"Message": "Image not found"}), 404

		img_link = result[0]['img_link']

		upload_folder = os.path.join(
			current_app.root_path,
			"uploads",
			"formation_img",
			f"formation_{formation_id}"
		)

		if not os.path.isfile(os.path.join(upload_folder, img_link)):
			return jsonify({"Message": "Image file not found on disk"}), 404

		return send_from_directory(upload_folder, img_link)

	except Exception as e:
		print(e)
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500
