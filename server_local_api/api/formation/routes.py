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


def _load_json_field(raw):
	"""Return None if the key was not sent (=> do not touch), else a list."""
	if raw is None:
		return None
	if isinstance(raw, (list, dict)):
		return raw
	try:
		return json.loads(raw or '[]')
	except (TypeError, ValueError):
		return []


def _formation_snapshot(formation_id):
	rows = Database.execute_query(
		"SELECT * FROM formation WHERE id = %s",
		[formation_id],
		fetch=True
	)
	if not rows:
		return None

	seasons_rows = Database.execute_query(
		"SELECT * FROM season WHERE formation_id = %s",
		[formation_id],
		fetch=True
	) or []

	subjects_rows = Database.execute_query(
		"SELECT * FROM formation_subject WHERE formation_id = %s",
		[formation_id],
		fetch=True
	) or []

	links_rows = Database.execute_query(
		"""
		SELECT sss.*
		FROM season_sub_subject sss
		JOIN season s ON s.id = sss.season_id
		WHERE s.formation_id = %s
		""",
		[formation_id],
		fetch=True
	) or []

	links_by_subject = {}
	for link in links_rows:
		links_by_subject.setdefault(link.get('formation_sub_subject'), []).append(link.get('season_id'))

	subjects_audit = []
	for s in subjects_rows:
		s = dict(s)
		s['season_ids'] = links_by_subject.get(s.get('id'), [])
		subjects_audit.append(s)

	snapshot = dict(rows[0])
	snapshot['seasons'] = [dict(s) for s in seasons_rows]
	snapshot['subjects'] = subjects_audit
	return snapshot


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
				acs.other_section AS section,
				al.other_level AS level,
				COUNT(s.id) AS sessions_count
			FROM formation f
			LEFT JOIN account_section acs ON acs.id = f.account_section_id
			LEFT JOIN account_level al ON al.id = f.account_level_id
			LEFT JOIN session s ON s.formation_id = f.id 
			WHERE f.account_id = %s
				AND f.enabled = 1
			GROUP BY f.id, f.name, f.description, f.type_session, f.number_day_duration,
				f.number_session, f.img_link, f.condition_of_passage, f.status, f.created_at,
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
		if not check_formation(formation_id):
			return jsonify({
				"Message": "There is no formation with this id"
			}), 404

		rows = Database.execute_query(
			"""
			SELECT
				f.id,
				f.account_id,
				f.account_level_id,
				f.account_section_id,
				f.name,
				f.description,
				f.status,
				f.type_date,
				f.other_type_date,
				f.type_session,
				f.other_type_session,
				f.number_day_duration,
				f.number_session,
				f.condition_of_passage,
				f.condition_of_passage_formule,
				f.condition_of_passage_formule_by_note,
				f.condition_of_passage_formule_by_present,
				f.condition_of_passage_formule_by_note_present,
				f.public_resource,
				f.img_link
			FROM formation f
			WHERE f.id = %s AND f.enabled = 1
			""",
			(formation_id,),
			fetch=True
		)

		if not rows:
			return jsonify({"Message": "There is no formation with this id"}), 404

		formation = dict(rows[0])

		# ------------------ Seasons ------------------
		seasons_rows = Database.execute_query(
			"""
			SELECT id, ref, title, description, type_duration, number_duration
			FROM season
			WHERE formation_id = %s
			ORDER BY id
			""",
			(formation_id,),
			fetch=True
		) or []

		# ------------------ Subjects ------------------
		subjects_rows = Database.execute_query(
			"""
			SELECT id, ref, account_sub_subject_id, description, number_hours
			FROM formation_subject
			WHERE formation_id = %s
			ORDER BY id
			""",
			(formation_id,),
			fetch=True
		) or []

		# ------------------ Subject -> season refs ------------------
		links_rows = Database.execute_query(
			"""
			SELECT sss.formation_sub_subject, s.ref
			FROM season_sub_subject sss
			JOIN season s ON s.id = sss.season_id
			WHERE s.formation_id = %s
			""",
			(formation_id,),
			fetch=True
		) or []

		refs_by_subject = {}
		for link in links_rows:
			refs_by_subject.setdefault(link['formation_sub_subject'], []).append(link['ref'])

		subjects = []
		for s in subjects_rows:
			s = dict(s)
			s['season_refs'] = refs_by_subject.get(s['id'], [])
			subjects.append(s)

		formation['seasons'] = [dict(s) for s in seasons_rows]
		formation['subjects'] = subjects

		# keep the list shape: the page reads formationArr[0]
		return jsonify([formation]), 200

	except Exception as e:
		current_app.logger.exception("view_formation failed")
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500


@formation_bp.route('/update_formation/<int:formation_id>', methods=['POST'])
def update_formation(formation_id):
	try:
		# Accept both JSON and multipart (multipart is needed for the image)
		if request.is_json:
			data = request.get_json() or {}
		else:
			data = request.form.to_dict()
		files = request.files

		old_record = Database.execute_query(
			"SELECT * FROM formation WHERE id = %s AND enabled = 1",
			(formation_id,),
			fetch=True
		)
		if not old_record:
			return jsonify({"Message": "Formation not found"}), 404
		old_record = old_record[0]

		# camelCase (payload) -> snake_case (DB column)
		# imgLink is not here on purpose: the image is only set through the file upload
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
		}

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
		}

		# Required columns: an empty value means "not changed", keep the old one
		required_fields = {'name', 'typeDate', 'typeSession'}

		fields_to_update = {}
		for k, v in data.items():
			if k not in field_map:
				continue

			if isinstance(v, str):
				v = v.strip()
				if k in nullable_fields:
					v = v or None

			if k in required_fields and not v:
				continue

			fields_to_update[field_map[k]] = v

		seasons_data = _load_json_field(data.get('seasons'))
		subjects_data = _load_json_field(data.get('subjects'))

		# ------------------ Snapshot BEFORE changes (for audit) ------------------
		old_audit = _formation_snapshot(formation_id)

		# ------------------ Image ------------------
		image_file = files.get('formation_logoFile')
		if image_file and image_file.filename:
			filename = secure_filename(image_file.filename)

			upload_folder = os.path.join(
				current_app.root_path,
				"uploads",
				"formation_img",
				f"formation_{formation_id}"
			)
			os.makedirs(upload_folder, exist_ok=True)
			image_file.save(os.path.join(upload_folder, filename))

			old_img = old_record.get('img_link')
			if old_img and old_img != filename:
				try:
					os.remove(os.path.join(upload_folder, old_img))
				except OSError:
					pass

			fields_to_update['img_link'] = filename

		if not fields_to_update and seasons_data is None and subjects_data is None:
			return jsonify({"Message": "No fields provided to update"}), 400

		# ------------------ Update formation row ------------------
		if fields_to_update:
			set_clause = ", ".join(f"{col} = %s" for col in fields_to_update.keys())
			values = list(fields_to_update.values())
			values.append(formation_id)

			Database.execute_query(
				f"UPDATE formation SET {set_clause}, updated_at = NOW() WHERE id = %s",
				values,
				fetch=False
			)

		account_id = old_record.get('account_id')

		# ------------------ Sync seasons (match by ref) ------------------
		if seasons_data is not None:
			existing = Database.execute_query(
				"SELECT id, ref FROM season WHERE formation_id = %s",
				[formation_id],
				fetch=True
			) or []
			existing_by_ref = {str(r['ref']): r['id'] for r in existing}
			incoming_refs = set()

			for s in seasons_data:
				ref = str(s.get('id_season_ref'))
				incoming_refs.add(ref)

				if ref in existing_by_ref:
					Database.execute_query(
						"""
						UPDATE season
						SET title = %s, description = %s, type_duration = %s, number_duration = %s
						WHERE id = %s
						""",
						[s.get('title'), s.get('description'), s.get('type'), s.get('duration'),
						 existing_by_ref[ref]],
						fetch=False
					)
				else:
					Database.execute_query(
						"""
						INSERT INTO season
							(formation_id, account_id, title, description, type_duration, number_duration, ref)
						VALUES (%s, %s, %s, %s, %s, %s, %s)
						""",
						[formation_id, account_id, s.get('title'), s.get('description'),
						 s.get('type'), s.get('duration'), s.get('id_season_ref')],
						fetch=False
					)

			for ref, season_id in existing_by_ref.items():
				if ref not in incoming_refs:
					Database.execute_query(
						"DELETE FROM season_sub_subject WHERE season_id = %s",
						[season_id],
						fetch=False
					)
					Database.execute_query(
						"DELETE FROM season WHERE id = %s",
						[season_id],
						fetch=False
					)

		# ------------------ Sync subjects + season links (match by ref) ------------------
		if subjects_data is not None:
			season_rows = Database.execute_query(
				"SELECT id, ref FROM season WHERE formation_id = %s",
				[formation_id],
				fetch=True
			) or []
			season_id_by_ref = {str(r['ref']): r['id'] for r in season_rows}

			existing = Database.execute_query(
				"SELECT id, ref FROM formation_subject WHERE formation_id = %s",
				[formation_id],
				fetch=True
			) or []
			existing_by_ref = {str(r['ref']): r['id'] for r in existing}
			incoming_refs = set()

			for sub in subjects_data:
				ref = str(sub.get('id_subject_ref'))
				incoming_refs.add(ref)

				if ref in existing_by_ref:
					subject_id = existing_by_ref[ref]
					Database.execute_query(
						"""
						UPDATE formation_subject
						SET account_sub_subject_id = %s, description = %s, number_hours = %s
						WHERE id = %s
						""",
						[sub.get('accountSubjectId'), sub.get('description'), sub.get('hours'), subject_id],
						fetch=False
					)
				else:
					subject_id = Database.execute_query(
						"""
						INSERT INTO formation_subject
							(account_sub_subject_id, formation_id, description, number_hours, ref)
						VALUES (%s, %s, %s, %s, %s)
						""",
						[sub.get('accountSubjectId'), formation_id, sub.get('description'),
						 sub.get('hours'), sub.get('id_subject_ref')],
						fetch=False
					)
					if not subject_id:
						return jsonify({"Message": "Formation not updated"}), 400

				# rebuild the links of this subject
				Database.execute_query(
					"DELETE FROM season_sub_subject WHERE formation_sub_subject = %s",
					[subject_id],
					fetch=False
				)
				for season_ref in (sub.get('seasons') or []):
					season_id = season_id_by_ref.get(str(season_ref))
					if season_id:
						Database.execute_query(
							"""
							INSERT INTO season_sub_subject (season_id, formation_sub_subject)
							VALUES (%s, %s)
							""",
							[season_id, subject_id],
							fetch=False
						)

			for ref, subject_id in existing_by_ref.items():
				if ref not in incoming_refs:
					Database.execute_query(
						"DELETE FROM season_sub_subject WHERE formation_sub_subject = %s",
						[subject_id],
						fetch=False
					)
					Database.execute_query(
						"DELETE FROM formation_subject WHERE id = %s",
						[subject_id],
						fetch=False
					)

		# ------------------ Audit ------------------
		new_audit = _formation_snapshot(formation_id)

		log_audit(
			table_name="formation_audit",
			action_type="UPDATE",
			old_data=old_audit or dict(old_record),
			new_data=new_audit or dict(data)
		)

		return jsonify({
			"Message": "Formation updated successfully",
			"formation_id": formation_id,
			"img_link": (new_audit or {}).get('img_link')
		}), 200

	except Exception as e:
		current_app.logger.exception("update_formation failed")
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
		public_resource = (data.get('publicResource') or '').strip() or None
		description = (data.get('description') or '').strip() or None

		# ------------------ Parse seasons & subjects JSON (not persisted yet) ------------------
		try:
			seasons_data = json.loads(data.get('seasons') or '[]')
		except (TypeError, ValueError):
			seasons_data = []

		try:
			subjects_data = json.loads(data.get('subjects') or '[]')
		except (TypeError, ValueError):
			subjects_data = []

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
		              img_link,
		              public_resource,
		              enabled,
		              created_at,
		              updated_at
		          ) VALUES (
		              %s,%s,%s,%s,%s,
		              1,
		              %s,%s,%s,%s,
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
			type_date,
			other_type_date,
			type_session,
			other_type_session,
			number_day_duration,
			number_session,
			img_link,
			public_resource
		]

		result = Database.execute_query(query, values, fetch=False)

		if not result:
			return jsonify({"Message": "Formation not created"}), 400

		formation_id = result
		# # ----------------- Insert Season ---------------

		for i in seasons_data:
			query_season = """
				INSERT INTO season
					(formation_id, account_id, title, description, type_duration, number_duration, ref)
				VALUES (%s, %s, %s, %s, %s, %s, %s)
			"""

			values = (formation_id, account_id, i.get('title'), i.get('description'), i.get('type'), i.get('duration'),
					  i.get('id_season_ref'))
			result = Database.execute_query(query_season, values, fetch=False)
			if not result:
				return jsonify({"Message": "Formation not created"}), 400

		# ----------------- Insert Subjects + season links ---------------

		for i in subjects_data:
			query_subject = """
				INSERT INTO formation_subject
				   (account_sub_subject_id, formation_id, description, number_hours, ref)
				VALUES (%s, %s, %s, %s, %s)
			"""
			values = (i.get('accountSubjectId'), formation_id, i.get('description'), i.get('hours'),
					  i.get('id_subject_ref'))
			formation_sub_subject_id = Database.execute_query(query_subject, values, fetch=False)
			if not formation_sub_subject_id:
				return jsonify({"Message": "Formation Not Created"}), 400

			for j in (i.get('seasons') or []):
				query_season_id = """
			        SELECT id
			        FROM season
			        WHERE ref = %s
			    """
				values = (j,)
				season_rows = Database.execute_query(query_season_id, values, fetch=True)
				for row in season_rows:
					query_season_sub_subject = """
				            INSERT INTO season_sub_subject
				                (season_id, formation_sub_subject)
				            VALUES (%s, %s)
				        """
					values = (row.get('id'), formation_sub_subject_id)
					result = Database.execute_query(query_season_sub_subject, values, fetch=False)

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

		# ------------------ Fetch final records for audit ------------------
		new_record = Database.execute_query(
			"SELECT * FROM formation WHERE id = %s",
			[formation_id],
			fetch=True
		)

		seasons_rows = Database.execute_query(
			"SELECT * FROM season WHERE formation_id = %s",
			[formation_id],
			fetch=True
		) or []

		subjects_rows = Database.execute_query(
			"SELECT * FROM formation_subject WHERE formation_id = %s",
			[formation_id],
			fetch=True
		) or []

		season_links_rows = Database.execute_query(
			"""
			SELECT sss.*
			FROM season_sub_subject sss
			JOIN season s ON s.id = sss.season_id
			WHERE s.formation_id = %s
			""",
			[formation_id],
			fetch=True
		) or []

		# attach the linked season ids to each subject
		links_by_subject = {}
		for link in season_links_rows:
			links_by_subject.setdefault(link.get('formation_sub_subject'), []).append(link.get('season_id'))

		subjects_audit = []
		for s in subjects_rows:
			s = dict(s)
			s['season_ids'] = links_by_subject.get(s.get('id'), [])
			subjects_audit.append(s)

		audit_data = dict(new_record[0]) if new_record else dict(data)
		audit_data['seasons'] = [dict(s) for s in seasons_rows]
		audit_data['subjects'] = subjects_audit

		log_audit(
			table_name="formation_audit",
			action_type="INSERT",
			old_data=None,
			new_data=audit_data
		)

		return jsonify({
			"Message": "Formation created successfully",
			"formation_id": formation_id,
			"img_link": img_link,
			"seasons": seasons_data,
			"subjects": subjects_data
		}), 200

	except Exception as e:
		print(e)
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
