from flask import Blueprint, jsonify, request
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database

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


@formation_bp.route('/get-formation-info/<int:account_id>',methods=['GET'])
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
				   f.condition_of_passage,
				   f.status
			 FROM formation f
			WHERE f.account_id = %s AND f.enabled = 1
		"""
		values = (account_id,)
		result = Database.execute_query(query,values)

		if result :
			return jsonify({
				"Data":result
			}),200
		else:
			return jsonify({
				"Message":"Error",
				"Data":[]
			}),404


	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from get_formation_info"
		}),500


@formation_bp.route('/delete_formation/<formation_id>/<int:account_id>',methods=['POST'])
def delete_formation(formation_id,account_id):
	try:
		if not(check_formation(formation_id)):
			return jsonify({
				"Message":"There is no formation with this id"
			}),404

		query = """
			UPDATE formation
			SET enabled = 0
			WHERE id = %s and account_id = %s
		"""
		values = (formation_id,account_id)
		result = Database.execute_query(query,values,fetch=False)
		if result:
			return jsonify({
				"Message":"Foramtion deleted with success"
			}),200
		else:
			return jsonify({
				"Message":"Failed to delete formation"
			}),400

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@formation_bp.route('/view_formation/<int:formation_id>',methods=['GET'])
def view_formation(formation_id):
	try:
		if not(check_formation(formation_id)):
			return jsonify({
				"Message":"There is no formation with this id"
			}),404
		query = """
		    SELECT 
				DISTINCT
				f.name,
				f.status,
				CASE 
					WHEN al.other_level IS NOT NULL THEN al.other_level
					ELSE l.name 
				END AS level_name,
				f.account_section_id,
				CASE
					WHEN ast.other_section IS NOT NULL THEN ast.other_section
					ELSE s.name
				END AS section_name,       -- ← missing this
				f.type_date,
				f.number_day_duration,
				f.number_session,
				f.type_session,
				f.condition_of_passage,
				f.public_resource,
				f.description
			FROM formation f
			JOIN account_level al    ON al.id  = f.account_level_id
			JOIN level_config l      ON l.id   = al.level_config_id
			JOIN account_section ast ON ast.id = f.account_section_id
			JOIN section_config s    ON s.id   = ast.section_config_id  -- ← also fixed: ast not act
			WHERE f.id = %s AND f.enabled = 1 AND s.enabled = 1  
		"""
		result = Database.execute_query(query,(formation_id,),fetch=True)
		return jsonify(result),200

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		})

@formation_bp.route('/update_formation/<int:formation_id>', methods=['POST'])
def update_formation(formation_id):
    try:
        data = request.get_json()

        # All updatable fields
        allowed_fields = [
            'name',
            'status',
            'type_date',
            'number_day_duration',
            'number_session',
            'type_session',
            'condition_of_passage',
            'public_resource',
            'description',
            'account_section_id',
            'account_level_id'
        ]

        # Build SET clause dynamically from only what was sent
        fields_to_update = {k: v for k, v in data.items() if k in allowed_fields}

        if not fields_to_update:
            return jsonify({"Message": "No fields provided to update"}), 400

        set_clause = ", ".join([f"{k} = %s" for k in fields_to_update.keys()])
        values     = list(fields_to_update.values())
        values.append(formation_id)  # for WHERE clause

        query = f"""
            UPDATE formation
            SET {set_clause},
                updated_at = NOW()
            WHERE id = %s
        """

        result = Database.execute_query(query, values, fetch=False)

        if result:
            return jsonify({"Message": "formation updated successfully"}), 200
        else:
            return jsonify({"Message": "Error updating formation"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500
