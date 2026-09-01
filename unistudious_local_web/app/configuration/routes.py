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
	get_all_tag_service,
	get_all_subject_config_service,
	delete_account_tag_service,
	get_account_tag_service,
	update_account_tag_service,
	get_all_completion_tag_serice,
	create_completion_tag_service,
	view_completion_tag_service,
	update_completion_tag_service,
	create_account_tag_service,
	delete_completion_tag_service,
	get_all_door_service,
	delete_door_service,
	update_door_service,
	view_door_service,
	create_door_service


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
		}),500


@configuration_bp.route('/api/create_account_config/<int:account_id>', methods=['POST'])
def create_account_config(account_id):
	try:
		data = request.get_json()
		status, response = create_account_level_service(data, account_id)
		return jsonify(response.json()), status
	except Exception as e:
		print(e)
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@configuration_bp.route('/api/delete_account_config/<int:account_id>/<int:account_level_id>',methods=['POST'])
def delete_account_level(account_id,account_level_id):
	try:
		status,response = delete_account_level_service(account_id,account_level_id)
		if response is None:
			return jsonify({"Message": "Error: could not reach remote server"}), 502
		return jsonify(response.json()),response.status_code
	except Exception as e:
		print(e)
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
		}),500

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
		}),500


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
		}),500

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
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500

@configuration_bp.route('/api/view_account_subject/<int:account_subject_id>',methods=['GET'])
def view_subject_config(account_subject_id):
	try:
		status,response = view_account_subject_service(account_subject_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500



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

@configuration_bp.route('/api/create_account_tag/<int:account_id>', methods=['POST'])
def create_account_tag(account_id):
	try:
		data = request.get_json()
		status, response = create_account_tag_service(account_id,data)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"Error in updating accountTag"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


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
		data = request.get_json(force=True)


		status,response = create_completion_tag_service(account_id,data)
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":f"Error in creating completion_tag"
			}),400
	except Exception as e:
		print(e)
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


# =============================================== DOORS ENDPOINTS ===============================================
@configuration_bp.route('/api/create_door', methods=['POST'])
def create_door():
	try:
		data = request.get_json()
		status,response = create_door_service(data)
		if status:
			return jsonify({
				"Message":"Succes in creating door"
			}),response.status_code
		else:
			return jsonify({
				"Message":"Error in creating door"
			}),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error {e} coming from backend"
		}),500

@configuration_bp.route('/api/get_all_doors', methods=['GET'])
def get_all_doors():
	try:
		status,response = get_all_door_service()
		if status:
			return jsonify(response.json()),response.status_code
		else:
			return jsonify({
				"Message":"Error in getting all door"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/update_door/<int:door_id>', methods=['POST'])
def api_update_door(door_id):
	try:

		payload = request.get_json()
		if not payload :
			return jsonify({
				"Message":"There is no data"
			}),500
		status,response = update_door_service(door_id,payload)
		if status:
			return jsonify({
				"Message":"Success in updating door"
			}),response.status_code
		else:
			return jsonify({
				"Message":"Error in updating door"
			}),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} in updating door"
		})

@configuration_bp.route('/api/delete_door/<int:door_id>',methods=['POST'])
def delete_door(door_id):
	try:
		status,response = delete_door_service(door_id)
		if status:
			return jsonify(response.json()), response.status_code
		else:
			return jsonify({
				"Message":"Error in deliting door"
			}),500
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@configuration_bp.route('/api/view_door/<int:door_id>', methods=['GET'])
def view_door(door_id):
	try:
		status, response = view_door_service(door_id)
		if status:
			return jsonify(response.json()), 200
		else:
			return jsonify({"Message": "There is no data for this door"}), 404
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} in view_door"
		}), 500