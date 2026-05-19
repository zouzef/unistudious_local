from flask import Blueprint, jsonify, request
import sys
import os
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

account_section_bp = Blueprint('account_section',__name__,url_prefix='/scl')

# ENDPOINT 1: Get account_section
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
        values = (account_id,)
        result = Database.execute_query(query, values, fetch=True)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({
                "Message": "There is no account_section with this account_id"
            }), 404

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# ENDPOINT 2: Create account_section
@account_section_bp.route('/create_account_section/<int:account_id>', methods=['POST'])
def create_account_section(account_id):
	try:
		data = request.get_json()
		section_id = data.get('sectionId')
		description = data.get('description') or None
		other = data.get('otherSection') or None

		# Validate required field
		if not section_id:
			return jsonify({
				"Message": "sectionId is required"
			}), 400

		query = """
            INSERT INTO account_section
            (account_id, section_config_id, status, description, other_section, enabled, created_at, timestamp)
            VALUES (%s, %s, 1, %s, %s, 1, NOW(), NOW())
        """
		values = (account_id, section_id, description, other)
		result = Database.execute_query(query, values, fetch=False)

		if result:
			return jsonify({
                "Message": "account_section created successfully"
			}), 200
		else:
			return jsonify({
                "Message": "account_section failed to create"  # Fix: was "account_sesction"
    		}), 400  # Fix: was missing status code

	except Exception as e:
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

# ENDPOINT 3: Delete account_section
@account_section_bp.route('/delete_account_section/<int:account_section_id>',methods=['POST'])
def delete_account_section(account_section_id):
	try:
		query ="""
			UPDATE account_section
			SET enabled = 0
			WHERE id = %s
		"""
		values = (account_section_id,)
		result = Database.execute_query(query,values,fetch=False)
		if result:
			return jsonify({
				"Message":"account section updated with success"
			}),200
		else:
			return jsonify({
				"Message":"There is no account_section with this id"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

# ENDPOINT 4: Update account_section
@account_section_bp.route('/update_account_section/<int:account_section_id>', methods=['POST'])
def update_account_section(account_section_id):
	try:
		data = request.get_json()
		section_id = data.get('sectionId')
		status = data.get('status')
		other = data.get('other') or None
		description = data.get('description') or None

		# Validate required fields
		if not section_id or status is None:
			return jsonify({
                "Message": "sectionId and status are required"
            }), 400

		query = """
            UPDATE account_section 
            SET section_config_id = %s,
                status = %s,
                description = %s,
                other_section = %s,
                enabled = 1,
                updated_at = NOW()
            WHERE id = %s
        """
		values = (section_id, status, description, other, account_section_id)
		result = Database.execute_query(query, values, fetch=False)

		if result:
			return jsonify({
                "Message": "account_section updated successfully"
            }), 200
		else:
			return jsonify({
                "Message": "Error in updating account_section"
            }), 400

	except Exception as e:
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500  # Fix: was missing status code

# ENDPOINT 5: View account_section
@account_section_bp.route('/view_account_section/<int:account_section_id>',methods=['GET'])
def view_account_section(account_section_id):
	try:
		query = """
			SELECT *
			FROM account_section
			WHERE id = %s AND enabled = 1
		"""

		values = (account_section_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({"Message":"There is no account_section with this id "}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

# ENDPOINT 6: Get subject_config
@account_section_bp.route('/get_section_config',methods=['GET'])
def get_section_config():
	try:
		query = """
			SELECT *
			FROM section_config 
			WHERE enabled = 1
		"""
		result = Database.execute_query(query,fetch=True)

		if result:
			return jsonify(
				result
			),200
		else:
			return jsonify({
				"Message":"There is no section_config"
			}),404

	except Exception as e:
		print(e)
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500