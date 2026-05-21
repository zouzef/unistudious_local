from flask import Blueprint, jsonify, request
from flask import send_file
import sys
import os
import json
from datetime import datetime, timedelta
import bcrypt
import mysql.connector
from flask import Blueprint, request,jsonify


# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# ========================================
# TAG ENDPOINTS
# ========================================


# Create blueprint
tag_bp = Blueprint('tag', __name__, url_prefix='/scl')

def check_exist_tag(tag_id):
	try:
		query = """
			SELECT count(*) AS nbr
			FROM tag_config 
			WHERE id = %s AND enabled = 1
		"""
		result = Database.execute_query(query,(tag_id,),fetch=True)
		return result[0]['nbr']>0
	except Exception as e:
		return False


@tag_bp.route('/get_all_tag',methods=['GET'])
def get_all_tag():
	try:
		query = """
			SELECT *
			FROM tag_config WHERE enabled = 1
		"""
		result = Database.execute_query(query,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({
				"Message":"There is no tag_config"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@tag_bp.route('/get_account_tag/<int:account_id>',methods=['GET'])
def get_account_tag(account_id):
	try:
		query = """
			SELECT
				at.id,
				at.status,
				at.description,
				at.public,
				CASE
					WHEN at.tag_config_id = 1 THEN at.other_tag
					ELSE tc.title
				END AS tag_name
			FROM account_tag at
			LEFT JOIN tag_config tc ON tc.id = at.tag_config_id
			WHERE at.account_id = %s AND at.enabled = 1
		"""
		result=Database.execute_query(query,(account_id,),fetch=True)
		if result:
			return jsonify(
				result
			),200
		else:
			return jsonify({
				"Message":"There is no account_config"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@tag_bp.route('/delete_account_tag/<int:account_tag_id>',methods=['POST'])
def delete_account_tag(account_tag_id):
	try:
		query = """
			UPDATE account_tag
			set enabled = 0
			WHERE id =%s
		"""
		result = Database.execute_query(query,(account_tag_id,),fetch=False)
		if result:
			return jsonify({
				"Message":"account_tag Delete with success"
			}),200
		else:
			return jsonify({
				"Message":"Error in deleting account_tag"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500

@tag_bp.route('/view_account_tag/<int:account_tag_id>',methods=['GET'])
def view_account_tag(account_tag_id):
	try:
		query = """
			SELECT *
			FROM account_tag 
			WHERE enabled = 1 AND id = %s
		"""
		result = Database.execute_query(query,(account_tag_id,),fetch=True)
		if result:
			return jsonify(
				result
			),200
		else:
			return jsonify({
				"Message":"There is no data for this id"
			}),404
	except Exception as e:
		return jsonify({
			"Message":f"Error {e} coming from server"
		}),500

@tag_bp.route('/edit_account_tag/<int:account_tag_id>', methods=['POST'])
def update_account_tag(account_tag_id):
	try:
		data = request.get_json()

		# ── Step 1: fetch current record ──────────────────────────────────
		current = Database.execute_query(
            "SELECT * FROM account_tag WHERE id = %s AND enabled = 1",
            (account_tag_id,),
            fetch=True
        )
		if not current:
			return jsonify({"Message": "Account tag not found"}), 404

		current = current[0]

		# ── Step 2: compare sent values vs current values ─────────────────
		fields_to_update = {}

		if str(data.get('tag_config_id')) != str(current['tag_config_id']):
			fields_to_update['tag_config_id'] = data.get('tag_config_id')

		if data.get('other_tag') != current['other_tag']:
			fields_to_update['other_tag'] = data.get('other_tag') or None

		if str(data.get('status')) != str(current['status']):
			fields_to_update['status'] = data.get('status')

		if str(data.get('public')) != str(current['public']):
			fields_to_update['public'] = data.get('public')

		if data.get('description') != current['description']:
			fields_to_update['description'] = data.get('description') or None

		# ── Step 3: nothing changed ───────────────────────────────────────
		if not fields_to_update:
			return jsonify({"Message": "No changes detected"}), 200

		# ── Step 4: build dynamic UPDATE query ───────────────────────────
		fields_to_update['updated_at'] = 'NOW()'

		set_clause = ', '.join([
            f"{col} = NOW()" if val == 'NOW()' else f"{col} = %s"
            for col, val in fields_to_update.items()
		])

		values = tuple(
            val for val in fields_to_update.values() if val != 'NOW()'
		)
		values += (account_tag_id,)

		query = f"""
            UPDATE account_tag
            SET {set_clause}
            WHERE id = %s
            AND enabled = 1
        """

		response = Database.execute_query(query, values, fetch=False)
		if response:
			return jsonify({"Message": "Account tag updated with success"}), 200
		else:
			return jsonify({"Message": "Account tag update failed"}), 400

	except Exception as e:
		return jsonify({"Message": f"Error: {e} coming from server"}), 500

@tag_bp.route('/create_account_tag/<int:account_id>',methods=['POST'])
def create_account_tag(account_id):
	try:
		data = request.get_json()
		if not data:
			return jsonify({"Message": "There is no data to insert it"}), 400

		tag_id = data.get('tag_id')
		visibility = data.get('visibility') or 1
		description = data.get('description') or None
		other_tag = data.get('other_tag') or None
		public = data.get('public')
		if not(check_exist_tag(tag_id)):
			return jsonify({
				"Message":"Error in tag_id"
			}),404

		query = """
			INSERT INTO account_tag 
			(
				account_id,
				tag_config_id,
				status,
				description,
				other_tag,
				public,
				enabled,
				created_at,
				timestamp
				)
			values(
				%s,
				%s,
				1,
				%s,
				%s,
				%s,
				1,
				NOW(),
				NOW())
		"""
		values=(account_id,tag_id,description,other_tag,public)
		result= Database.execute_query(query,values,fetch=False)
		if result:
			return jsonify({"Message": "account_tag created with success"}), 200
		else:
			return jsonify({"Message": "account_tag creation failed"}), 400


	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500