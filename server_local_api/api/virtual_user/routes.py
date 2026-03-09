from flask import Blueprint,jsonify, request
import uuid
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


# ========================================
# Virtual User Endpoints
# ========================================

#create blueprint
Vusers_bp = Blueprint('virtual_users', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Get virtual users by account and session
# ========================================
@Vusers_bp.route('/get-all-virtuel-user/<int:account_id>',methods=['GET'])
def get_all_virtuel_user(account_id):
	try:
		query = """
			SELECT 
				id,
				user_id,
				name,
				created_by_id,
				phone,
				email,
				data
			FROM virtual_user 
			WHERE enabled = 1 AND account_id = %s
		"""
		values = (account_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify({
				"Message":"Success",
				"data":result
			}),200
		else:
			return jsonify({
				"Message":"There is no data from this account_id",
				"Data":[]
			}),404
	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from get all_virtuel_users"
		}),500


# ========================================
# ENDPOINT 2: Delete virtual user by id
# ========================================
@Vusers_bp.route('/delete-virtuel-user/<int:id>',methods=['POST'])
def delete_virtuel_user(id):
	try:
		query = """
			UPDATE virtual_user
			 set enabled = 0 , slc_edit = 1
			 where id = %s
			 
		"""
		values = (id,)
		result = Database.execute_query(query,values,fetch=False)
		return jsonify({
			"Message":"Virtuel_user deleted "
		}),200

	except Exception as e:
		return jsonify({
			"Message":f"Error : {e} coming from delete virtuel user"
		}),500


# ========================================
# ENDPOINT 3: Update Virtual user by id
# ========================================
@Vusers_bp.route('/update-virtual-user/<int:id>', methods=['POST'])
def update_virtuel_user(id):
	try:
		data = request.get_json()

		name   = data.get('name')
		email  = data.get('email')
		phone  = data.get('phone')
		status = data.get('status')  # expected: 1 (active) or 0 (inactive)
		query = """
            UPDATE virtual_user
            SET
                name       = %s,
                email      = %s,
                phone      = %s,
                status     = %s,
                slc_edit   = 1,
                updated_at = NOW()
            WHERE id = %s
        """
		values = (name, email, phone, status, id)
		Database.execute_query(query, values, fetch=False)

		return jsonify({
		    "message": "Virtual user updated successfully"
		}), 200

	except Exception as e:
		return jsonify({
			"message": f"Error: {e} coming from update virtual user"
		}), 500


# ========================================
# ENDPOINT 4: Create virtual user
# ========================================

def create_user(data):
	try:
		username =  data.get('username')
		email = data.get('email')


	except Exception as e:
		return None


@Vusers_bp.route('/create_virtual_user', methods=['POST'])
def create_virtual_user():
	try:
		data = request.get_json()
		name = data.get('name')
		email = data.get('email')
		phone = data.get('phone')
		status = data.get('status')
		new_uuid = str(uuid.uuid4())

		if not name or not email or not phone or not status:
			return jsonify({
				"Message":"Missing name, email, phone or status"
			}),400

		query = """
			
		"""
		values = (name, email, phone, status)
		Database.execute_query(query, values, fetch=False)
		return jsonify({
			"Message":"Virtual user created successfully"
		}),200
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from create_virtual_user"
		}),500