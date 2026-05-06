from flask import Blueprint, jsonify, request
from flask import send_file
import sys
import os
import json
from datetime import datetime, timedelta
import bcrypt
import mysql.connector
from flask import Blueprint, request,jsonify

# from server_local_api.api.calendar.test import result

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# ========================================
# GROUP/USER MANAGEMENT ENDPOINTS
# ========================================


# Create blueprint
users_bp = Blueprint('users', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Get groups with students by account and session
# ========================================

@users_bp.route('/get-group/<int:account_id>/<int:session_id>', methods=['GET'])
# @token_required
def get_group(account_id, session_id):
	try:
		# Get groups with students in one query
		query = """
                    SELECT 
                        g.id,
                        g.session_id,
                        g.local_id,
                        g.name,
                        g.capacity,
                        g.status,
                        u.id as user_id,
                        u.username,
                        u.full_name,
                        u.email,
                        u.phone,
                        r.id as relation_id
                    FROM relation_group_local_session g
                    LEFT JOIN relation_user_session r 
                        ON r.relation_group_local_session_id = g.id 
                        AND r.enabled = 1
                    LEFT JOIN user u 
                        ON u.id = r.user_id 
                        AND u.enabled = 1
                    WHERE g.session_id = %s 
                        AND g.account_id = %s 
                        AND g.enabled = 1 
                        AND g.special_group IS NULL
                    ORDER BY g.id, u.username
                    LIMIT 1000  -- Add reasonable limit
                """
		results = Database.execute_query(query, (session_id, account_id))

		# Group the results by group_id
		groups = {}

		for row in results:
			group_id = row['id']

			# Create group entry if it doesn't exist
			if group_id not in groups:
				groups[group_id] = {
					'id': row['id'],
					'session_id': row['session_id'],
					'local_id': row['local_id'],
					'name': row['name'],
					'capacity': row['capacity'],
					'status': row['status'],
					'list_student': []
				}

			# Add student if exists (LEFT JOIN may return NULL)
			if row['user_id']:
				groups[group_id]['list_student'].append({
					'user_id': row['user_id'],
					'username': row['username'],
					'full_name': row['full_name'],
					'email': row['email'],
					'phone': row['phone'],
					'relation_id': row['relation_id']
				})

		# Convert dictionary to list
		groups_list = list(groups.values())

		print(f"Found {len(groups_list)} groups")

		return jsonify({
			"success": True,
			"data": groups_list,
			"count": len(groups_list)
		}), 200

	except Exception as err:
		print(f"Error: {err}")
		return jsonify({
			"success": False,
			"message": str(err),
			"data": [],
			"count": 0
		}), 500


# ========================================
# TEACHER ENDPOINTS
# ========================================

# ========================================
# ENDPOINT 2: Get teachers by session
# ========================================
@users_bp.route('/get_teacher/<int:group_id>', methods=['GET'])
# @token_required
def get_teacher(group_id):
	try:
		query = """
            SELECT 
                u.id as user_id, 
                u.username, 
                u.email, 
                u.full_name, 
                u.phone, 
                u.img_link,
                rtsg.subject_id,
                CASE 
                    WHEN sc.name = 'Other' THEN acs.other_subject
                    ELSE sc.name
                END as subject_name
            FROM user u
            INNER JOIN relation_teacher_to_subject_group rtsg 
                ON rtsg.user_id = u.id 
                AND rtsg.relation_group_local_session_id = %s
                AND rtsg.enabled = 1
            INNER JOIN subject_config sc 
                ON sc.id = rtsg.subject_id
            LEFT JOIN account_subject acs
                ON acs.subject_config_id = rtsg.subject_id
                AND acs.enabled = 1
            WHERE u.enabled = 1 
            AND (JSON_CONTAINS(u.roles, '"ROLE_TEACHER"') OR JSON_CONTAINS(u.roles, '"ROLE_ADMIN"'))
        """

		teachers = Database.execute_query(query, (group_id,))

		return jsonify({"Message": "Success", "data": teachers}), 200

	except Exception as e:
		print(f"Error: {e} coming from get_teacher")
		return jsonify({"Message": f"Error {e} coming from server"}), 500


@users_bp.route('/get_teacher_session/<int:session_id>', methods=['GET'])
# @token_required
def get_teacher_session(session_id):
	try:
		query = """
            SELECT 
                u.id as user_id, 
                u.username, 
                u.email, 
                u.full_name, 
                u.phone, 
                u.img_link,
                GROUP_CONCAT(
                    DISTINCT CASE 
                        WHEN sc.name = 'Other' THEN acs.other_subject
                        ELSE sc.name
                    END
                    ORDER BY sc.name
                    SEPARATOR ', '
                ) as subjects,
                GROUP_CONCAT(DISTINCT rtsg.subject_id ORDER BY rtsg.subject_id SEPARATOR ',') as subject_ids
            FROM user u
            INNER JOIN relation_teacher_to_subject_group rtsg 
                ON rtsg.user_id = u.id 
                AND rtsg.enabled = 1
            INNER JOIN relation_group_local_session rgls
                ON rgls.id = rtsg.relation_group_local_session_id
                AND rgls.session_id = %s
            INNER JOIN subject_config sc 
                ON sc.id = rtsg.subject_id
            LEFT JOIN account_subject acs
                ON acs.subject_config_id = rtsg.subject_id
                AND acs.enabled = 1
            WHERE u.enabled = 1 
            AND (JSON_CONTAINS(u.roles, '"ROLE_TEACHER"') OR JSON_CONTAINS(u.roles, '"ROLE_ADMIN"'))
            GROUP BY 
                u.id, 
                u.username, 
                u.email, 
                u.full_name, 
                u.phone, 
                u.img_link
        """

		teachers = Database.execute_query(query, (session_id,))
		print("result: ",teachers)
		return jsonify({"Message": "Success", "data": teachers}), 200

	except Exception as e:
		print(f"Error: {e} coming from get_teacher")
		return jsonify({"Message": f"Error {e} coming from server"}), 500


@users_bp.route('/get_all_teachers',methods=['GET'])
def get_all_teachers():
	try:
		query = """
		    SELECT u.username, u.id	, email, full_name, roles , img_link ,status
		    FROM user u
		    WHERE u.enabled = 1 AND
		    (JSON_CONTAINS(u.roles, '"ROLE_TEACHER"') OR JSON_CONTAINS(u.roles, '"ROLE_ADMIN"'))
		    
		"""
		result = Database.execute_query(query,fetch=True)
		if result :
			return jsonify({
				"Message":"Success",
				"Data":result
			}),200
		else:
			return jsonify({
				"Message":"There is no Teacher"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e}",

		}),500



# ========================================
# ENDPOINT 3: Affect user to group
# ========================================
@users_bp.route('/affect_user_group/<int:session_id>', methods=['POST'])
# @token_required
def affect_user_group_endpoint(session_id):
	try:
		# Get JSON data from request
		data = request.get_json()
		print(f"Received data: {data}")
		print(f"Session ID: {session_id}")

		# Extract specific fields
		user_id = data.get('user_id')
		group_id = data.get('group_id')

		print(f"User ID: {user_id}, Group ID: {group_id}")

		# Validate
		if not user_id or not group_id:
			return jsonify({
				"status": "error",
				"message": "Missing user_id or group_id"
			}), 400

		# Check if user exists
		query = """
            SELECT COUNT(id) as nbr FROM user WHERE id = %s AND enabled = 1
        """
		result = Database.execute_query(query, (user_id,))

		if not result or result[0]['nbr'] == 0:
			print(f"User {user_id} not found")
			return jsonify({
				"status": "error",
				"message": "User not found"
			}), 404

		print(f"User {user_id} exists")

		# Check if group exists
		query = """
            SELECT COUNT(id) as nbr FROM relation_group_local_session
            WHERE id = %s AND enabled = 1
        """
		result = Database.execute_query(query, (group_id,))

		if not result or result[0]['nbr'] == 0:
			print(f"Group {group_id} not found")
			return jsonify({
				"status": "error",
				"message": "Group not found"
			}), 404

		print(f"Group {group_id} exists")

		# Update user's group assignment
		query = """
            UPDATE relation_user_session
            SET relation_group_local_session_id = %s
            WHERE user_id = %s 
                AND session_id = %s 
                AND relation_group_local_session_id IS NULL
                AND enabled = 1
            ORDER BY id ASC
            LIMIT 1
        """
		Database.execute_query(query, (group_id, user_id, session_id), fetch=False)

		print(f"User assigned to group successfully")
		return jsonify({
			"status": "success",
			"message": f"User assigned to group successfully",
			"data": {
				"user_id": user_id,
				"group_id": group_id,
				"session_id": session_id
			}
		}), 200

	except Exception as e:
		print(f"Error: {e}")
		return jsonify({
			"status": "error",
			"message": f"Error: {str(e)}"
		}), 500


# =============================================
# ENDPOINT 4: Get users not affected to groups
# =============================================
@users_bp.route('/user_not_affected/<int:session_id>/<int:account_id>', methods=['GET'])
# @token_required
def get_user_not_affected(session_id, account_id):
	try:
		# Validate session exists and belongs to this account
		query = """
            SELECT id, name 
            FROM session 
            WHERE id = %s AND account_id = %s AND enabled = 1
        """
		session_data = Database.execute_query(query, (session_id, account_id))

		if not session_data:
			return jsonify({
				"status": "error",
				"message": "Session not found."
			}), 404

		# Get users NOT assigned to groups with relation IDs
		query = """
            SELECT 
                r.id as relation_id,
                r.user_id,
                u.full_name,
                u.username
            FROM relation_user_session r
            INNER JOIN user u ON u.id = r.user_id
            WHERE r.enabled = 1 
                AND u.enabled = 1 
                AND r.session_id = %s
                AND (r.relation_group_local_session_id IS NULL 
                     OR r.relation_group_local_session_id = 0)
            ORDER BY u.full_name
        """
		relations = Database.execute_query(query, (session_id,))

		# Group by user and build response
		users = {}

		for relation in relations:
			user_id = relation['user_id']

			if user_id not in users:
				users[user_id] = {
					'userId': user_id,
					'userName': relation['full_name'] or relation['username'],
					'sessionId': session_id,
					'sessionName': session_data[0]['name'],
					'sessionCount': 1,
				}
			else:
				users[user_id]['sessionCount'] += 1

		# Convert to list
		students = list(users.values())

		print(f"Users not affected to groups: {students}")

		return jsonify({"students": students}), 200

	except Exception as e:
		print(f"Error: {e}")
		return jsonify({
			"status": "error",
			"message": "Unexpected error occurred."
		}), 500


# =============================================
# ENDPOINT 5: Delete group
# =============================================
@users_bp.route('/delete-group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
	try:
		print(group_id)
		# Disable the group
		query = """ 
            UPDATE relation_group_local_session
            SET enabled = 0
            WHERE id = %s     
        """
		values = (group_id,)
		result = Database.execute_query(query, values)
		# Check if any rows were affected
		if result == 0 or (isinstance(result, dict) and result.get('rowcount', 0) == 0):
			return jsonify({"Message": "Group not found"}), 404

		# Remove group association from users
		query2 = """
            UPDATE relation_user_session 
            SET relation_group_local_session_id = NULL 
            WHERE relation_group_local_session_id = %s
        """
		Database.execute_query(query2, values, fetch=False)

		return jsonify({"Message": "Group deleted successfully"}), 200

	except Exception as e:
		print(f"Error: {e} coming from delete group")
		return jsonify({"Message": f"Error: {str(e)}"}), 500


# =============================================
# ENDPOINT 6: Create group
# =============================================
@users_bp.route('/create_group/<int:session_id>', methods=['POST'])
def create_group(session_id):
	try:
		data = request.get_json()

		# Validate required fields
		if (not data.get('group_name') or not data.get('capacity')
				or not data.get('subject_id') or not data.get('teacher_id')
				or not data.get('account_id') or not data.get('local_id')):
			return jsonify({"Message": "Missing required fields"}), 400

		# Extract data
		local_id = data['local_id']
		account_id = data['account_id']
		name = data['group_name']
		capacity = data['capacity']
		subject_id = data['subject_id']
		teacher_id = data['teacher_id']
		status = 1
		enabled = 1
		special_group = data.get('special_group', None)  # Will be None if not provided
		access_type = data.get('access_type', 0)

		current_time = datetime.now()
		print(f"Creating group at: {current_time}")

		# Insert group
		query = """
            INSERT INTO relation_group_local_session 
            (session_id, local_id, account_id, name, capacity, status, enabled, created_at, timestamp, special_group, access_type, slc_use)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, 1)
        """
		values = (session_id, local_id, account_id, name, capacity, status, enabled, special_group, access_type)

		result = Database.execute_query(query, values, fetch=False)

		# Get the last inserted ID
		if isinstance(result, int):
			group_id = result
		elif isinstance(result, dict) and 'lastrowid' in result:
			group_id = result['lastrowid']
		elif isinstance(result, dict) and 'id' in result:
			group_id = result['id']
		else:
			group_id = None

		# Insert teacher-subject relationship
		query2 = """
            INSERT INTO relation_teacher_to_subject_group
            (relation_group_local_session_id, subject_id, user_id, enabled, created_at, timestamp, slc_use)
            VALUES (%s, %s, %s, 1, NOW(), NOW(), 1)
        """
		values2 = (group_id, subject_id, teacher_id)
		Database.execute_query(query2, values2, fetch=False)

		return jsonify({
			"Message": "Group created successfully",
			"group_id": group_id
		}), 201

	except Exception as e:
		print(f"Error: {e} coming from create-group")
		return jsonify({"Message": f"Error: {str(e)}"}), 500


# =============================================
# ENDPOINT 7: Get all users / Get all users (virtuel)
# =============================================
@users_bp.route('/get-all-users/<int:account_id>', methods=['GET'])
def get_all_user(account_id):
	try:

		query = """
            SELECT DISTINCT
                u.username, u.full_name,u.email,u.phone, u.img_link, u.id,u.isvirtual, rus.session_id
            FROM user u, relation_user_session rus
            WHERE u.enabled = 1 
            AND rus.session_id IN (SELECT s.id FROM session s WHERE s.account_id = %s)
            AND rus.user_id = u.id 
            ORDER BY u.created_at DESC
        """
		response = Database.execute_query(query, (account_id,), fetch=True)
		return jsonify({
			"Message": "Success",
			"data": response
		}), 200

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from get_all_users"
		}), 500


# =============================================
# ENDPOINT 8: Update User
# =============================================
@users_bp.route('/update-user/<int:id>', methods=['POST'])
def update_user(id):
    try:
        # Check user exists
        result = Database.execute_query("SELECT COUNT(*) as nbr FROM user WHERE id = %s", (id,))
        if result[0]['nbr'] == 0:
            return jsonify({"Message": "User not found"}), 404

        data = request.get_json()

        # ── Map allowed fields: payload_key → database_column ────
        allowed_fields = {
            'name':        'username',
            'email':       'email',
            'phone':       'phone',
            'status':      'status',
            'full_name':   'full_name',
            'address':     'address',
            'birth_place': 'birth_place',
            'birth_date':  'birth_date',
            'grand':       'grand',
            'roles':       'roles',
        }

        # ── Build SET clause only from fields present in request ─
        set_clauses = []
        values = []

        for payload_key, db_column in allowed_fields.items():
            if payload_key in data:
                value = data[payload_key]

                # ✅ Convert empty strings to None (NULL in MySQL)
                if value == '' or value is None:
                    value = None

                set_clauses.append(f"{db_column} = %s")
                values.append(value)

        if not set_clauses:
            return jsonify({"Message": "No fields to update"}), 400

        # ── Always update these ───────────────────────────────────
        set_clauses.append("slc_edit = 1")
        set_clauses.append("updated_at = NOW()")

        values.append(id)  # for WHERE id = %s

        query = f"UPDATE user SET {', '.join(set_clauses)} WHERE id = %s"

        Database.execute_query(query, tuple(values), fetch=False)

        return jsonify({"Message": "user updated successfully"})

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from update_user"}), 500

# =============================================
# ENDPOINT 9: Delete user
# =============================================
@users_bp.route('/delete-user/<int:id>',methods=['POST'])
def delete_user(id):
	try:

		query = """
					SELECT COUNT(*) as nbr FROM user WHERE id = %s
				"""
		values = (id,)
		result = Database.execute_query(query, values)
		if result[0]['nbr'] == 0:
			return jsonify({
				"Message": "User not found"
			}), 404


		query = """
			UPDATE user 
			SET enabled = 0 , slc_edit = 1
			WHERE id = %s
		"""
		values = (id,)
		result = Database.execute_query(query,values,fetch=False)
		return jsonify({
			"Message":"user delete with success"
		}),200
	except Exception as e:
		return jsonify({
			"Message":"Error: {e} coming from the delete user"
		}),500


# =============================================
# ENDPOINT 9: Get Profile image of user
# =============================================
@users_bp.route('/get-profile-image/<int:user_id>', methods=['GET'])
def get_profile_file(user_id):
	try:
		query = """
            SELECT username, img_link FROM user WHERE id = %s
        """
		values = (user_id,)
		result = Database.execute_query(query, values, fetch=True)

		if not result:
			# User not found - return default image
			default_img_path = os.path.join(
				os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
				'static/assets/images/user-profile.png'
			)
			return send_file(default_img_path)

		img_filename = result[0]['img_link']

		# If user has no image set, return default
		if not img_filename or img_filename.strip() == '':
			default_img_path = os.path.join(
				os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
				'static/assets/images/user-profile.png'
			)
			return send_file(default_img_path)

		BASE_UPLOAD_FOLDER = os.path.join(
			os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
			f'uploads/user_img/user_{user_id}'
		)
		img_path = os.path.join(BASE_UPLOAD_FOLDER, img_filename)

		# If image file doesn't exist, return default
		if not os.path.exists(img_path):
			print(f"⚠️ Image not found at {img_path}, returning default")
			default_img_path = os.path.join(
				os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
				'static/assets/images/user-profile.png'
			)
			return send_file(default_img_path)

		return send_file(img_path)

	except Exception as e:
		print(f"Error: {e} coming from get_user_image")
		# Return default image on error instead of 500
		try:
			default_img_path = os.path.join(
				os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
				'static/assets/images/profile.svg'
			)
			return send_file(default_img_path)
		except:
			return jsonify({"message": "Error loading image"}), 500


# =============================================
# ENDPOINT 10: Affect user to session
# =============================================



# =============================================
# ENDPOINT 11: User authetificate
# =============================================
import json

@users_bp.route('/Authentificate-Teacher', methods=['POST'])
def authentification_teacher():
	try:
		data = request.get_json()
		if not data:
			return jsonify({
                "Message": "Error: Teacher Data is Missing"
            }), 400

		username = data.get("username")
		password = data.get("password")

		if not username or not password:
			return jsonify({
                "Message": "Error: Username or Password Missing"
            }), 422

		# 1. Fetch user from DB by username
		query = "SELECT username, password, roles FROM user WHERE username = %s"
		user = Database.execute_query(query, (username,), fetch=True)

		# 2. Check if user exists
		if not user:
			return jsonify({
                "Message": "Error: User Not Found"
            }), 404

		# 3. Verify password against Symfony bcrypt hash ($2y$ → $2b$)
		hashed_password = user[0]["password"].replace("$2y$", "$2b$")
		password_match = bcrypt.checkpw(
			password.encode("utf-8"),
			hashed_password.encode("utf-8")
		)

		if not password_match:
			return jsonify({
                "Message": "Error: Invalid Password"
            }), 401

		# 4. Check role — must be ROLE_TEACHER or ROLE_ADMIN
		roles = json.loads(user[0]["roles"])  # "[\"ROLE_TEACHER\"]" → ["ROLE_TEACHER"]

		allowed_roles = {"ROLE_TEACHER", "ROLE_ADMIN"}
		if not allowed_roles.intersection(set(roles)):
			return jsonify({
                "Message": "Error: Access Denied — Not a Teacher or Admin"
            }), 403

		# 5. Success
		return jsonify({
            "Message": "Authentication Successful",
            "username": user[0]["username"],
            "roles": roles
        }), 200

	except Exception as e:
		print(f"Error in authentification_teacher : {e}")
		return jsonify({
            "Message": "Error coming from server",
            "Error": str(e)
        }), 500


# =============================================
# ENDPOINT 11: GET Manager info
# =============================================
@users_bp.route('/get-manager-info',methods=['GET'])
def get_manager_info():
	try:
		query = """
			SELECT
			 	id,username,roles,email,full_name,phone,address
			 FROM user 
			WHERE roles LIKE '%ROLE_MANAGER_ADMINISTRATIVE%' AND enabled = 1;
		"""
		result= Database.execute_query(query,fetch=True)
		if result:
			return jsonify({
				"Data": result
			}), 200
		else:
			return jsonify({
				"Message":"There is no role manager"
			}),404

	except Exception as e:
		print(f"Error: {e} coming from server")
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


# =============================================
# ENDPOINT 12: GET User info
# =============================================
@users_bp.route('/get_user_info/<int:user_id>',methods=['GET'])
def get_user_info(user_id):
	try:
		query = """
			SELECT
			 	id, username,email,full_name, roles, img_link, status, phone,grand,birth_place,birth_date ,address 
			FROM user 
			WHERE id = %s AND enabled = 1 
		"""
		values = (user_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify({
				"Data":result
			}),200
		else:
			return jsonify({
				"Message":"There is no id for this user"
			}),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


# =============================================
# ENDPOINT 13: CREATE user
# =============================================
@users_bp.route('/create_user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "Message": "There is no data to create user"
            }), 400

        valid_columns = {
            "account_id", "username", "email", "full_name", "roles",
            "img_link", "reset_token", "status", "created_by", "password",
            "birth_date", "birth_place", "phone", "address", "grand",
            "access_type", "access_type_date", "enabled", "updated_at",
            "uuid", "facebook_id", "google_id", "mastodon_access_token",
            "general_notification", "message_notification", "calendar_notification",
            "push_notification", "sms_notification", "login_notification",
            "horsline", "ref_slc", "apple_id", "open_source_user_name",
            "rocket_chat_user_id", "fcm_web", "fcm_android", "fcm_ios",
            "releaseToken", "useToken", "slc_use", "isvirtual", "slc_edit", "id_user"
        }

        filtered_data = {k: v for k, v in data.items() if k in valid_columns}

        if not filtered_data:
            return jsonify({
                "Message": "No valid fields provided to create user"
            }), 400

        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join(["%s"] * len(filtered_data))
        values = list(filtered_data.values())

        query = f"INSERT INTO user ({columns}) VALUES ({placeholders})"

        result = Database.execute_query(query, values, fetch=False)
        if result:
            return jsonify({
                "Message": "User created successfully"
            }), 200

        return jsonify({
            "Message": "User not created"
        }), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# =============================================
# ENDPOINT 14: CREATE Teacher
# =============================================
@users_bp.route('/create_teacher',methods=['POST'])
def create_teacher():
	try:
		print("this endpoint not created yet")
		return jsonify({
			"Message":"this endpoint not created yet ! "
		}),200
	except Exception as e:
		return jsonify({
			"Message":f"Error:{e} coming from server"
		})
