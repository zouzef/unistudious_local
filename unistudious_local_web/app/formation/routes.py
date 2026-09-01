from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response

from app.formation.service import (
	fetch_formation_info,
	create_formation_service,
	get_all_foramtion_service,
	delete_formation_service,
	view_formation_service,
	update_formation_service,
	get_formation_image_service
)


formation_bp = Blueprint('formation', __name__)


@formation_bp.route('/api/get-formation-info/<int:account_id>', methods=['GET'])
def get_formation_info(account_id):
	try:
		status, formation_info = fetch_formation_info(account_id)
		if status and formation_info:
			return jsonify(formation_info), 200  # ← fixed
		else:
			return jsonify({"Message": "Error"}), 404
	except Exception as e:
		return jsonify({"Message": f"Error: {e} coming from get_formation_info"}), 500


@formation_bp.route('/api/create_formation/<int:account_id>', methods=['POST'])
def create_formation(account_id):
	try:
		form = request.form

		data = {
			'name': form.get('formation[name]'),
			'accountLevel': form.get('formation[accountLevel]'),
			'accountSection': form.get('formation[accountSection]'),
			'typeDate': form.get('formation[typeDate]'),
			'otherTypeDate': form.get('formation[otherTypeDate]'),
			'numberDayDuration': form.get('formation[numberDayDuration]'),
			'numberSession': form.get('formation[numberSession]'),
			'typeSession': form.get('formation[typeSession]'),
			'otherTypeSession': form.get('formation[otherTypeSession]'),
			'conditionOfPassage': form.get('formation[conditionOfPassage]'),
			'conditionOfPassageFormule': form.get('formation[conditionOfPassageFormule]'),
			'conditionOfPassageFormuleByNote': form.get('formation[conditionOfPassageFormuleByNote]'),
			'conditionOfPassageFormuleByPresent': form.get('formation[conditionOfPassageFormuleByPresent]'),
			'conditionOfPassageFormuleByNotePresent': form.get('formation[conditionOfPassageFormuleByNotePresent]'),
			'publicResource': form.get('formation[publicResource]'),
			'description': form.get('formation[description]'),
		}
		print(data)

		if not data.get('name'):
			return jsonify({"Message": "Missing required fields"}), 400

		files = None
		if 'formation_logoFile' in request.files:
			file = request.files['formation_logoFile']
			print(f"[local create_formation] received file: {file.filename!r}")  # debug — remove later
			if file.filename != '':
				files = {
					# read() instead of file.stream — avoids sending an
					# empty/consumed stream if anything upstream touched it
					'formation_logoFile': (file.filename, file.read(), file.mimetype)
				}

		success, result = create_formation_service(account_id, data, files)

		if success:
			return jsonify({
				"Message": "Formation created successfully",
				"data": result
			}), 200

		return jsonify({
			"Message": "Error creating formation",
			"Error": result
		}), 400

	except Exception as e:
		import traceback
		traceback.print_exc()
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500


@formation_bp.route('/api/get_all_formation/<int:account_id>', methods=['GET'])
def get_all_formation(account_id):
	try:
		status, response = get_all_foramtion_service(account_id)
		if status:
			return jsonify(response.json()), response.status_code
		else:
			return jsonify({
				"Message": "There is no data"
			}), 400
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500


@formation_bp.route('/api/delete_formation/<int:account_id>/<int:formation_id>', methods=['POST'])
def delete_formation(account_id, formation_id):
	try:
		status, response = delete_formation_service(formation_id, account_id)
		if status:
			return jsonify(response.json()), response.status_code
		else:
			return jsonify({"Message": "Error in deleting formation"}), 400
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500


@formation_bp.route('/api/view_formation/<int:formation_id>', methods=['GET'])
def view_formation(formation_id):
	try:
		status, response = view_formation_service(formation_id)
		if status:
			return jsonify(response.json()), response.status_code
		else:
			return jsonify({
				"Message": "There is no data for this fomation"
			}), 400

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		})


@formation_bp.route('/api/update_formation/<int:formation_id>', methods=['POST'])
def update_formation(formation_id):
	try:
		data = request.get_json()

		status, response = update_formation_service(formation_id, data)
		if status:
			return jsonify(response.json()), response.status_code
		else:
			return jsonify({
				"Message": f"Error in updating formation"
			}), 400
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500


@formation_bp.route('/api/get_formation_image/<int:formation_id>', methods=['GET'])
def get_formation_image(formation_id):
	try:
		success, image_bytes, content_type = get_formation_image_service(formation_id)

		if not success:
			return jsonify({"Message": "Image not found"}), 404

		return Response(image_bytes, mimetype=content_type)

	except Exception as e:
		print(e)
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500



