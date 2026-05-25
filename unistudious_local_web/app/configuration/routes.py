from http.client import responses

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import time
import os

from app.configuration.service import (
	get_account_level_service,
	get_level_service,
	create_account_level_service,
	delete_account_level_service,
	view_account_level_service,
	update_account_level_servie,
	get_account_section_service,
	create_account_section_service,
	delete_account_section_service,
	update_account_section_service,
	view_account_section_service,
	get_section_config_service,
	get_account_subject_service,
	delete_account_subject_service,
	get_subject_service,
	create_subject_config_service,
	update_subject_config_service,
	view_account_subject_service,
	get_all_foramtion_service,
	delete_formation_service,
	view_formation_service,
	update_formation_service,
	create_formation_service,
	get_all_tag_service,
	get_all_subject_config_service,
	delete_account_tag_service,
	get_account_tag_service,
	update_account_tag_service,
	get_all_completion_tag_serice,
	create_completion_tag_service,
	view_completion_tag_service,
	update_completion_tag_service,
	delete_completion_tag_service
)



configuration_bp = Blueprint('configuration',__name__)

@configuration_bp.route('/api/get_all_account_level/<int:account_id>',methods=['GET'])
def get_account_level(account_id):
	try:
		status,response = get_account_level_service(account_id)
		if status :
			return jsonify(response.json()),response.status_code
		else:
			return jsonify(response.json()),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})


@configuration_bp.route('/api/create_account_config/<int:account_id>', methods=['POST'])
def create_account_config(account_id):
	try:
		data = request.get_json()
		status, response = create_account_level_service(data, account_id)
		return jsonify(response.json()), status  # 👈 use .json() and return status directly
	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@configuration_bp.route('/api/delete_account_config/<int:account_id>/<int:account_level_id>',methods=['POST'])
def delete_account_level(account_id,account_level_id):
	try:
		status,response = delete_account_level_service(account_id,account_level_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend "
		}),500

@configuration_bp.route('/api/view_account_config/<int:account_level_id>',methods=['GET'])
def view_account_config(account_level_id):
	try:
		status,response = view_account_level_service(account_level_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@configuration_bp.route('/api/update_account_config/<int:account_level_id>',methods=['POST'])
def update_account_config(account_level_id):
	try:
		data = request.get_json()
		status,response= update_account_level_servie(data,account_level_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/get_all_level',methods=['GET'])
def get_all_level():
	try:
		status,response = get_level_service()
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

# =============================================== SECTION CONFIG ENDPOINTS ===============================================
@configuration_bp.route('/api/get_all_account_section/<int:account_id>',methods=['GET'])
def get_all_section_config(account_id):
	try:
		status,response = get_account_section_service(account_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/create_account_section/<int:account_id>', methods=['POST'])
def create_account_section(account_id):
	try:
		data        = request.get_json()
		section_id  = data.get('sectionId')

		if not section_id:
			return jsonify({
                "Message": "Missing section id"
            }), 400

		description = data.get('description') or None
		other       = data.get('otherSection') or None

		status, response = create_account_section_service(data, account_id)
		return jsonify(response.json()), response.status_code

	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@configuration_bp.route('/api/delete_account_section/<int:account_section_id>', methods=['POST'])
def delete_account_section(account_section_id):
	try:
		status, response = delete_account_section_service(account_section_id)
		return jsonify(response.json()), response.status_code
	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@configuration_bp.route('/api/update_account_section/<int:account_section_id>',methods=['POST'])
def update_account_section(account_section_id):
	try:
		data = request.get_json()
		status,response = update_account_section_service(data,account_section_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/view_account_section/<int:account_section_id>',methods=['GET'])
def view_account_section(account_section_id):
	try:
		status,response = view_account_section_service(account_section_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@configuration_bp.route('/api/get_section_config',methods=['GET'])
def get_section_config():
	try:
		status,response = get_section_config_service()
		return jsonify(response.json()),response.status_code

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})


# =============================================== ACCOUNT SUBJECT CONFIG ENDPOINTS ===============================================
@configuration_bp.route('/api/get_account_subject/<int:account_id>',methods=['GET'])
def get_account_subject(account_id):
	try:
		status,response=get_account_subject_service(account_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@configuration_bp.route('/api/delete_account_subject/<int:account_subject_id>', methods=['POST'])
def delete_account_subject(account_subject_id):
	try:
		status, response = delete_account_subject_service(account_subject_id)
		return jsonify(response.json()), response.status_code
	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

@configuration_bp.route('/api/get_subject', methods=['GET'])
def get_subject():
	try:
		status, response = get_subject_service()
		return jsonify(response.json()), response.status_code
	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

@configuration_bp.route('/api/create_account_subject/<int:account_id>',methods=['POST'])
def create_account_subject(account_id):
	try:
		data = request.get_json()
		subject_id = data.get('subjectId')
		description = data.get('description') or None
		other = data.get('otherSubject') or None
		if not(subject_id):
			return jsonify({
				"Message":"Missing to select subject_id"
			}),402


		status,response = create_subject_config_service(data,account_id)
		return jsonify(response.json()),response.status_code

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from the backend "
		})

@configuration_bp.route('/api/update_account_subject/<int:account_subject_id>', methods=['POST'])
def update_subject(account_subject_id):
    try:
        data          = request.get_json()
        subject_id    = data.get('subjectId')      # ← fix key
        status        = data.get('status') or 1
        description   = data.get('description') or None
        other_subject = data.get('otherSubject') or None

        if not subject_id:
            return jsonify({"Message": "Missing subject_id"}), 400

        status, response = update_subject_config_service(data, account_subject_id)
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from backend"}), 500

@configuration_bp.route('/api/view_account_subject/<int:account_subject_id>',methods=['GET'])
def view_subject_config(account_subject_id):
	try:
		status,response = view_account_subject_service(account_subject_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})


# =============================================== FORMATION ENDPOINTS ===============================================
@configuration_bp.route('/api/get_all_formation/<int:account_id>',methods=['GET'])
def get_all_formation(account_id):
	try:
		status,response = get_all_foramtion_service(account_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"There is no data"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/delete_formation/<int:account_id>/<int:formation_id>',methods=['POST'])
def delete_formation(account_id,formation_id):
	try:
		status,response = delete_formation_service(formation_id,account_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({"Message":"Error in deleting formation"}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/view_formation/<int:formation_id>',methods=['GET'])
def view_formation(formation_id):
	try:
		status,response = view_formation_service(formation_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"There is no data for this fomation"
			}),500

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@configuration_bp.route('/api/update_formation/<int:formation_id>',methods=['POST'])
def update_session(formation_id):
	try:
		data = request.get_json()

		status,response=update_formation_service(formation_id,data)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":f"Error in updating formation"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/create_formation/<int:account_id>', methods=['POST'])
def create_formation(account_id):
	try:
		img_link = None
		file = request.files.get('formation_logoFile')

		if file and file.filename != '':
			filename  = secure_filename(file.filename)
			# Add timestamp to avoid duplicate filenames
			unique_filename = f"{int(time.time())}_{filename}"
			save_path = os.path.join(current_app.root_path, '..', 'static', 'assets', 'images', 'formations', unique_filename)
			os.makedirs(os.path.dirname(save_path), exist_ok=True)
			file.save(save_path)
			img_link = f'/static/assets/images/formations/{unique_filename}'

		# ── 2. Collect form fields ──────────────────────────────────
		payload = {
            'name':                                    request.form.get('formation[name]'),
            'status':                                  request.form.get('formation[status]'),
            'accountLevel':                            request.form.get('formation[accountLevel]'),
            'accountSection':                          request.form.get('formation[accountSection]'),
            'typeDate':                                request.form.get('formation[typeDate]'),
            'otherTypeDate':                           request.form.get('formation[otherTypeDate]'),
            'numberDayDuration':                       request.form.get('formation[numberDayDuration]'),
            'numberSession':                           request.form.get('formation[numberSession]'),
            'typeSession':                             request.form.get('formation[typeSession]'),
            'otherTypeSession':                        request.form.get('formation[otherTypeSession]'),
            'conditionOfPassage':                      request.form.get('formation[conditionOfPassage]'),
            'conditionOfPassageFormule':               request.form.get('formation[conditionOfPassageFormule]'),
            'conditionOfPassageFormuleByNote':         request.form.get('formation[conditionOfPassageFormuleByNote]'),
            'conditionOfPassageFormuleByPresent':      request.form.get('formation[conditionOfPassageFormuleByPresent]'),
            'conditionOfPassageFormuleByNotePresent':  request.form.get('formation[conditionOfPassageFormuleByNotePresent]'),
            'publicResource':                          request.form.get('formation[publicResource]'),
            'description':                             request.form.get('formation[description]'),
            'imgLink':                                 img_link,
		}

		# ── 3. Forward to local server ──────────────────────────────
		status, response = create_formation_service(account_id, payload)

		if status:
			return jsonify(response.json()), response.status_code
		else:
			return jsonify({"Message": "Error creating formation"}), 400

	except Exception as e:
		print(f"error: {e}")
		return jsonify({"Message": f"Error: {e} coming from backend"}), 500

# =============================================== TAG ENDPOINTS ===============================================
@configuration_bp.route('/api/get_tag_config',methods=['GET'])
def get_tag_confg():
	try:
		status,response = get_all_tag_service()
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":f"Error coming from server"
			})
	except Exception as e:
		print(e)
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/get_account_tag/<int:account_id>',methods=['GET'])
def get_account_tag(account_id):
	try:
		status,response = get_all_subject_config_service(account_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"There is no data for this account_id"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/delete_account_tag/<int:account_tag_id>',methods=['POST'])
def delete_account_tag(account_tag_id):
	try:
		status,response = delete_account_tag_service(account_tag_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({"Message":"Error in deleting tag_account"}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/view_account_tag/<int:account_tag_id>',methods=['GET'])
def view_account_tag(account_tag_id):
	try:
		status,response = get_account_tag_service(account_tag_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":f"There is no data for this account_tag_id"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@configuration_bp.route('/api/update_account_tag/<int:account_tag_id>', methods=['POST'])
def api_update_account_tag(account_tag_id):
    try:
        if not account_tag_id:
            return jsonify({"Message": "Account tag ID is required"}), 400

        data = request.get_json()

        status, response = update_account_tag_service(account_tag_id, data)
        if status:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({
                "Message": "Error in updating account tag"
            }), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from backend"
        }), 500


# =============================================== COMPLETION TAG ENDPOINTS ===============================================
@configuration_bp.route('/api/get_completion_tag/<account_id>',methods=['GET'])
def get_completion_tag(account_id):
	try:
		status,response = get_all_completion_tag_serice(account_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"Error in getting all completion_tag"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@configuration_bp.route('/api/delete_completion_tag/<int:completion_tag_id>',methods=['POST'])
def delete_completion_tag(completion_tag_id):
	try:
		status,response = delete_completion_tag_service(completion_tag_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"Error in deleting completion_tag"
			}),400

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@configuration_bp.route('/api/update_completion_tag/<int:completion_tag_id>', methods=['POST'])
def update_completion_tag(completion_tag_id):
	try:
		data = request.get_json()
		status,response = update_completion_tag_service(completion_tag_id,data)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"Error in updating completion_tag"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from the backend"
		}),500

@configuration_bp.route('/api/view_completion_tag/<int:completion_tag_id>', methods=['GET'])
def view_completion_tag(completion_tag_id):
	try:
		status,response = view_completion_tag_service(completion_tag_id)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"There is no completion_tag"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@configuration_bp.route('/api/create_completion_tag/<int:account_id>', methods=['POST'])
def create_completion_tag(account_id):
	try:
		data = request.get_json()
		status,response = create_completion_tag_service(account_id,data)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":f"Error in creating completion_tag"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500