from flask import Blueprint, jsonify, request
import sys
import os
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


account_level_bp = Blueprint('account_level',__name__, url_prefix='/scl')

# ENDPOINT 1 : Get_account_level
@account_level_bp.route('/get_account_level/<int:account_id>',methods=['GET'])
def get_account_level(account_id):
	try:
		query = """
			SELECT DISTINCT
				a.*,
				COALESCE(a.other_level, lc.name) AS level_name
			FROM account_level a
			LEFT JOIN level_config lc ON a.level_config_id = lc.id
			WHERE a.account_id = %s 
			  AND a.enabled = 1
			
		"""
		values = (account_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({
				"Message":f"There is no level for this account"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

# ENDPOINT 2: Create account_level
@account_level_bp.route('/create_account_level/<int:account_id>',methods=['POST'])
def create_account_level(account_id):
	try:
		data = request.get_json()

		query = """
		    INSERT INTO account_level (account_id, level_config_id, description, enabled, created_at, timestamp, slc_edit)
		    VALUES (%s, %s, %s, 1, NOW(), NOW(), 1)
		"""
		values = (
			data.get('account_id'),
			data.get('level_config_id'),
			data.get('description') or None
		)
		response = Database.execute_query(query,values,fetch=False)
		if response:
			return jsonify({
				"Message":f"Account_level created with success"
			}),200
		else:
			return jsonify({
				"Message":f"Error in creating account_level"
			}),400

	except Exception as e:
		print(e)
		return jsonify({
			"Message":f"Error: {e} coming ffrom server"
		}),500

# ENDPOINT 3: delete account_level
@account_level_bp.route('/delete_account_level/<int:account_id>/<int:id_account_level>',methods=['POST'])
def delete_account_level(account_id,id_account_level):
	try:
		query = """
			UPDATE account_level 
			SET enabled = 0
			WHERE account_id = %s AND id = %s 
		"""
		values = (account_id,id_account_level)
		response = Database.execute_query(query,values,fetch=False)
		if response:
			return jsonify({
				"Message":"account_level created with success"
			}),200
		else:
			return jsonify({
				"Message":"Error in creating account_level"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

# ENDPOINT 4: View account_level
@account_level_bp.route('/view_account_level/<int:account_level_id>')
def view_account_level(account_level_id):
	try:
		query ="""
			SELECT * FROM account_level 
			WHERE id = %s AND enabled = 1
		"""
		values = (account_level_id,)
		response = Database.execute_query(query,values,fetch=True)
		if response:
			return jsonify(response),200
		else:
			return jsonify({"Message":"There is no account_level with this id"}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

# ENDPOINT 5: Edit account_level
@account_level_bp.route('/edit_account_level/<int:account_level_id>', methods=['POST'])  # 👈 missing methods
def update_account_level(account_level_id):
	try:
		data = request.get_json()

		level_config_id = data.get('level_config_id')  # 👈 was data.get('description') by mistake
		status          = data.get('status')
		description     = data.get('description') or None

		query = """
            UPDATE account_level
            SET level_config_id = %s,
                status = %s,
                description = %s,
                updated_at = NOW(),
                slc_edit = 1
            WHERE id = %s
            AND enabled = 1
        """
		values = (level_config_id, status, description, account_level_id)

		response = Database.execute_query(query, values, fetch=False)
		if response:
			return jsonify({
                "Message": "Account level updated with success"
            }), 200
		else:
			return jsonify({
                "Message": "Account level update failed"
            }),400

	except Exception as e:
		return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

# ENDPOINT 2: Get_all_level
@account_level_bp.route('/get_all_level', methods=['GET'])
def get_all_level():
	try:
		query = "SELECT * FROM level_config WHERE enabled = 1"
		result = Database.execute_query(query, fetch=True)

		if result:
			return jsonify(result), 200  # ✅ just pass result directly
		else:
			return jsonify({"message": "There is no level"}), 404

	except Exception as e:
		return jsonify({"message": f"Error: {e} coming from server"}), 500


