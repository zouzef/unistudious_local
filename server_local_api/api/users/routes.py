from flask import Blueprint, jsonify, request
from flask import send_file
import sys
import os
import json
from datetime import datetime, timedelta
import bcrypt
import mysql.connector
from flask import Blueprint, request,jsonify
import uuid
import random
import string


# from server_local_api.api.calendar.test import result

# Add parent directories to path
import uuid as uuid_lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required
from core.checks import *
# ========================================
# GROUP/USER MANAGEMENT ENDPOINTS
# ========================================


# Create blueprint
users_bp = Blueprint('users', __name__, url_prefix='/scl')



"""_______________________________________________________ Manager ENDPOINT _______________________________________________________"""
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


ALLOWED_MANAGER_ROLES = {
    "ROLE_MANAGER_CONFIG",
    "ROLE_MANAGER_FINANCE",
    "ROLE_MANAGER_HR",
    "ROLE_MANAGER_IT",
    "ROLE_MANAGER_MARKETING",
    "ROLE_CUSTOMER_MANAGER_SERVICE",
    "ROLE_MANAGER_ADMINISTRATIVE",
}
@users_bp.route('/create_manager/<int:account_id>', methods=['POST'])
def create_manager(account_id):
    try:
        data = request.form.to_dict()
        files = request.files

        full_name = data.get("fullName")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not username or not email or not password:
            return jsonify({
                "Message": "fullName, username, email and password are required"
            }), 400

        location = data.get("location")
        phone_number = data.get("phone_number")

        # roles can arrive either as a single field "roles" or repeated "roles[]"
        roles = request.form.getlist("roles[]")
        if not roles:
            single_role = data.get("roles")
            if single_role:
                roles = [single_role]

        if not roles:
            return jsonify({
                "Message": "roles is required"
            }), 400

        # Validate every role against the allowed manager roles
        invalid_roles = [r for r in roles if r not in ALLOWED_MANAGER_ROLES]
        if invalid_roles:
            return jsonify({
                "Message": f"Invalid role(s): {', '.join(invalid_roles)}"
            }), 400

        img_link = None
        image_file = files.get("image")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "managers")
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
            img_link = f"/static/uploads/managers/{filename}"

        user_data = {
            "account_id": account_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "roles": json.dumps(roles),
            "password": password,
            "phone": phone_number,
            "address": location,
            "status": 1,
            "enabled": 1,
        }
        if img_link:
            user_data["img_link"] = img_link

        filtered_data = {k: v for k, v in user_data.items() if v is not None}

        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join(["%s"] * len(filtered_data))
        values = list(filtered_data.values())

        query = f"INSERT INTO user ({columns}) VALUES ({placeholders})"
        result = Database.execute_query(query, values, fetch=False)

        if not result:
            return jsonify({"Message": "Manager not created"}), 400

        # ── Audit log ──────────────────────────────────────────────────
        # role column stores the primary/first role for routing purposes
        # (same pattern as ROLE_TEACHER in create_teacher)
        primary_role = roles[0]

        audit_payload = dict(filtered_data)
        audit_payload["id"] = result
        audit_payload["roles"] = roles  # store as list in the JSON payload too

        audit_query = """
            INSERT INTO user_audit (user_id, role, action_type, payload, is_synced)
            VALUES (%s, %s, %s, %s, %s)
        """
        Database.execute_query(
            audit_query,
            [result, primary_role, "CREATE", json.dumps(audit_payload), 0],
            fetch=False
        )

        return jsonify({
            "Message": "Manager created successfully",
            "user_id": result
        }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500



"""_______________________________________________________ Teacher ENDPOINT _______________________________________________________"""
@users_bp.route('/get_teacher/<int:group_id>', methods=['GET'])
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
		print("result: ", teachers)
		return jsonify({"Message": "Success", "data": teachers}), 200

	except Exception as e:
		print(f"Error: {e} coming from get_teacher")
		return jsonify({"Message": f"Error {e} coming from server"}), 500


@users_bp.route('/get_all_teachers', methods=['GET'])
def get_all_teachers():
	try:
		query = """
		    SELECT u.username, u.id	, email, full_name, roles , img_link ,status
		    FROM user u
		    WHERE u.enabled = 1 AND
		    (JSON_CONTAINS(u.roles, '"ROLE_TEACHER"') OR JSON_CONTAINS(u.roles, '"ROLE_ADMIN"'))

		"""
		result = Database.execute_query(query, fetch=True)
		if result:
			return jsonify({
				"Message": "Success",
				"Data": result
			}), 200
		else:
			return jsonify({
				"Message": "There is no Teacher"
			}), 404

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e}",

		}), 500


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


@users_bp.route('/create_teacher/<int:account_id>', methods=['POST'])
def create_teacher(account_id):
    try:
        data = request.form.to_dict()
        files = request.files

        full_name = data.get("fullName")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not username or not email or not password:
            return jsonify({
                "Message": "fullName, username, email and password are required"
            }), 400

        location = data.get("location")
        phone_number = data.get("phone_number")

        allowed_permission_access = request.form.getlist("allowedPermissionAccess[]")
        allowed_access_session = request.form.getlist("allowedAccessSession[]")

        img_link = None
        image_file = files.get("image")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "teachers")
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
            img_link = f"/static/uploads/teachers/{filename}"

        user_data = {
            "account_id": account_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "roles": json.dumps(["ROLE_TEACHER"]),
            "password": password,
            "phone": phone_number,
            "address": location,
            "status": 1,
            "enabled": 1,
        }
        if img_link:
            user_data["img_link"] = img_link

        filtered_data = {k: v for k, v in user_data.items() if v is not None}

        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join(["%s"] * len(filtered_data))
        values = list(filtered_data.values())

        query = f"INSERT INTO user ({columns}) VALUES ({placeholders})"
        result = Database.execute_query(query, values, fetch=False)

        if not result:
            return jsonify({"Message": "Teacher not created"}), 400

        # ── Insert into relation_teacher_account ─────────────────────────
        relation_uuid = str(uuid_lib.uuid4())

        relation_data = {
            "account_id": account_id,
            "user_id": result,           # id_user of the just-created teacher
            "status": 1,
            "enabled": 1,
            "uuid": relation_uuid,
            "release_token": 0,
            "access_permissions": json.dumps(allowed_permission_access),
            "access_session": json.dumps(allowed_access_session),
        }

        relation_columns = ", ".join(relation_data.keys())
        relation_placeholders = ", ".join(["%s"] * len(relation_data))
        relation_values = list(relation_data.values())

        relation_query = f"INSERT INTO relation_teacher_account ({relation_columns}) VALUES ({relation_placeholders})"
        relation_result = Database.execute_query(relation_query, relation_values, fetch=False)

        if not relation_result:
            # user row was created but the relation failed — log it, don't hard-fail the whole request
            logger.error("Teacher user_id=%s created but relation_teacher_account insert failed", result)

        # ── Audit log ──────────────────────────────────────────────────
        audit_query = """
            INSERT INTO user_audit (user_id, role, action_type, payload, is_synced)
            VALUES (%s, %s, %s, %s, %s)
        """
        audit_payload = dict(filtered_data)
        audit_payload["allowedPermissionAccess"] = allowed_permission_access
        audit_payload["allowedAccessSession"] = allowed_access_session
        audit_payload["relation_teacher_account_id"] = relation_result

        Database.execute_query(
            audit_query,
            [result, "ROLE_TEACHER", "CREATE", json.dumps(audit_payload), 0],
            fetch=False
        )

        return jsonify({
            "Message": "Teacher created successfully",
            "user_id": result,
            "relation_teacher_account_id": relation_result
        }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# =============================================
# ENDPOINT 15: check Teacher open door
# =============================================
def get_account_id(doorId):
	try:

		query = """
			SELECT s.account_id
			FROM slc_local s, slc_door d 
			WHERE d.slc_id = s.slc_id
			AND d.mac_id = %s
			AND d.enabled = 1
			AND s.enabled = 1
		"""
		accountId = Database.execute_query(query,(doorId,),fetch=True)[0]['account_id']

		return accountId

	except Exception as e:
		return None

def check_role_user(rfid, account_id):

	query = """
       SELECT roles
       FROM user 
       WHERE account_id = %s AND door_id = %s AND enabled = 1
    """

	result = Database.execute_query(query, (account_id, rfid))
	if not result:
		# ❌ No allowed role → check relation_teacher_account by account_id + door_id

		relation_query = """
		        SELECT user_id
		        FROM relation_teacher_account
		        WHERE account_id = %s AND door_id = %s AND enabled = 1 AND status = 1
		    """
		relation_result = Database.execute_query(relation_query, (account_id, rfid))
		if not relation_result:
			return False

		teacher_id = relation_result[0]['user_id']
		return teacher_id

	roles_raw = result[0]['roles']
	if not roles_raw:
		return False


	roles = json.loads(roles_raw) if isinstance(roles_raw, str) else roles_raw
	allowed = {"ROLE_ADMIN", "ROLE_MANAGER_ADMINISTRATIVE", "ROLE_MANAGER_CONFIG"}

	# ✅ Has an allowed role → return True directly
	if any(role in allowed for role in roles):
		return True

def check_calander_teacher(teacher_id, time, date):
	try:
		query = """
            SELECT teacher_id
            FROM relation_calander_group_session
            WHERE teacher_id = %s 
            AND DATE(start_time) = %s 
            AND TIME(%s) BETWEEN TIME(start_time) AND TIME(end_time)
            AND enabled = 1
        """
		values = (teacher_id, date, time)  # ✅ date first, time second
		result = Database.execute_query(query, values)  # ✅ fixed typo
		return len(result) > 0

	except Exception as e:
		return False

@users_bp.route('/check_teacher_access/<string:rfid>', methods=['POST'])
def check_teacher_access(rfid):
	try:

		data = request.get_json()
		date = data.get("date")
		time = data.get("time")
		doorId = data.get("Door_Mac_Id")
		account_id = get_account_id(doorId)
		if not account_id:
			return jsonify({"Message": "There is no door id in this local"}), 404

		role_result = check_role_user(rfid, account_id)

		if role_result is False:
			return jsonify({"Message": "Access denied"}), 403

		if role_result is True:
			return jsonify({"Message": f"Access for user with id: {rfid}","Status": True}), 200
		else:
			teacher_id = role_result
			if check_calander_teacher(teacher_id, time, date):
				return jsonify({"Message": "Teacher have access", "Status": True}), 200
			else:
				return jsonify({"Message": "Teacher doesn't have access", "Status": False}), 403

	except Exception as e:
		return jsonify({"Message": f"Error: {e}"}), 500



"""_______________________________________________________ STUDENT ENDPOINTS _______________________________________________________"""
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

		status_map = {"active": 1, "inactive": 0, "banned": 2}
		if "status" in filtered_data:
			val = filtered_data["status"]
			if isinstance(val, str):
				filtered_data["status"] = status_map.get(val.lower(), 1)

		columns = ", ".join(filtered_data.keys())
		placeholders = ", ".join(["%s"] * len(filtered_data))
		values = list(filtered_data.values())

		query = f"INSERT INTO user ({columns}) VALUES ({placeholders})"

		result = Database.execute_query(query, values, fetch=False)
		if result:


			# Determine primary role
			role = filtered_data.get("roles", "ROLE_USER")

			if isinstance(role, list):
				role = role[0] if role else "ROLE_USER"


			# Write audit record
			audit_query = """
			        INSERT INTO user_audit (user_id, role, action_type, payload, is_synced)
			        VALUES (%s, %s, %s, %s, %s)
			    """

			Database.execute_query(
				audit_query,
				[result, role, "CREATE", json.dumps(filtered_data), 0],
				fetch=False
			)
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
# ENDPOINT 8: Update User
# =============================================
@users_bp.route('/update-user/<int:id>', methods=['POST'])
def update_user(id):
    try:
        # Check user exists + grab current role for audit purposes
        result = Database.execute_query(
            "SELECT COUNT(*) as nbr, roles FROM user WHERE id = %s",
            (id,)
        )
        # NOTE: COUNT(*) + roles in the same row only works if there's exactly
        # one match — safer as two separate lookups:
        exists = Database.execute_query("SELECT COUNT(*) as nbr FROM user WHERE id = %s", (id,))
        if exists[0]['nbr'] == 0:
            return jsonify({"Message": "User not found"}), 404

        user_row = Database.execute_query("SELECT roles FROM user WHERE id = %s", (id,))
        current_roles = user_row[0]['roles'] if user_row else None

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
        updated_payload = {}  # for audit — only the fields actually changed

        for payload_key, db_column in allowed_fields.items():
            if payload_key in data:
                value = data[payload_key]

                # ✅ Convert empty strings to None (NULL in MySQL)
                if value == '' or value is None:
                    value = None

                set_clauses.append(f"{db_column} = %s")
                values.append(value)
                updated_payload[db_column] = value

        if not set_clauses:
            return jsonify({"Message": "No fields to update"}), 400

        # ── Always update these ───────────────────────────────────
        set_clauses.append("slc_edit = 1")
        set_clauses.append("updated_at = NOW()")

        values.append(id)  # for WHERE id = %s

        query = f"UPDATE user SET {', '.join(set_clauses)} WHERE id = %s"

        Database.execute_query(query, tuple(values), fetch=False)

        # ── Audit log ──────────────────────────────────────────────
        # Use the new role from this update if roles was changed, otherwise fall back
        # to the role the user already had.
        audit_role = updated_payload.get('roles', current_roles)

        audit_payload = dict(updated_payload)
        audit_payload["id"] = id

        audit_query = """
            INSERT INTO user_audit (user_id, role, action_type, payload, is_synced)
            VALUES (%s, %s, %s, %s, %s)
        """
        Database.execute_query(
            audit_query,
            [id, audit_role, "UPDATE", json.dumps(audit_payload), 0],
            fetch=False
        )

        return jsonify({"Message": "user updated successfully"})

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from update_user"}), 500


# =============================================
# ENDPOINT 7: Get all users / Get all users (virtuel)
# =============================================
@users_bp.route('/get-all-users/<int:account_id>', methods=['GET'])
def get_all_user(account_id):
	try:
		# --- Real users ---
		base_real_query = """
             SELECT DISTINCT u.id, u.full_name, u.phone, u.email, u.status, u.account_id
             FROM user u
             JOIN relation_user_session rus ON rus.user_id = u.id AND rus.enabled = 1
             JOIN session s ON s.id = rus.session_id AND s.enabled = 1
             WHERE u.isvirtual = 0
         """

		real_users = Database.execute_query(
			base_real_query + " AND s.account_id = %s", (account_id,), fetch=True
		)

		users = []
		real_user_ids = set()

		for u in real_users:
			uid = u['id']
			if uid in real_user_ids:
				continue
			real_user_ids.add(uid)

			# ── Attach linked VirtualUser (if any) for this real user + account ──
			virtual_query = """
                SELECT id, name, phone, email, status, account_id
                FROM virtual_user
                WHERE user_id = %s AND account_id = %s AND enabled = 1
            """
			virtual_result = Database.execute_query(virtual_query, (uid, account_id), fetch=True)
			virtual = virtual_result[0] if virtual_result else None

			users.append({
				'id': uid,
				'fullName': u['full_name'],
				'phone': u['phone'],
				'email': u['email'],
				'status': u['status'],
				'account': u['account_id'],
				'type': 'real',
				'action': 'edit_real',
				'virtualUser': {
					'id': virtual['id'],
					'fullName': virtual['name'],
					'phone': virtual['phone'],
					'email': virtual['email'],
					'status': virtual['status'],
					'account': virtual['account_id'],
				} if virtual else None,
			})

		# --- Virtual users ---
		base_virtual_query = """
             SELECT DISTINCT vu.id, vu.name, vu.phone, vu.email, vu.status, vu.account_id,
                    u.id AS real_id, u.full_name AS real_full_name, u.email AS real_email
             FROM virtual_user vu
             JOIN user u ON u.id = vu.user_id
             WHERE vu.enabled = 1
         """

		virtual_users = Database.execute_query(
			base_virtual_query + " AND vu.account_id = %s", (account_id,), fetch=True
		)

		for vu in virtual_users:
			real_id = vu['real_id']
			if real_id in real_user_ids:
				continue
			real_user_ids.add(real_id)
			users.append({
				'id': vu['id'],
				'userId': real_id,
				'fullName': vu['name'],
				'phone': vu['phone'],
				'email': vu['email'],
				'status': vu['status'],
				'account': vu['account_id'],
				'type': 'virtual',
				'action': 'edit_virtual',
				'realUser': {
					'id': real_id,
					'fullName': vu['real_full_name'],
					'email': vu['real_email'],
				},
			})

		users.sort(key=lambda x: (x['fullName'] or '').strip().lower())
		return jsonify({
			"Message": "Success",
			"data": users
		}), 200

	except Exception as e:
		print(e)
		return jsonify({
			"Message": f"Error: {e} coming from get_all_users"
		}), 500


# =============================================
# ENDPOINT 8: CREATE User
# =============================================
@users_bp.route('/create_student/<int:account_id>', methods=['POST'])
def create_student(account_id):
    try:
       data = request.form.to_dict()
       files = request.files

       selected_sessions = request.form.getlist("allowedAccessSession[]")
       full_name = data.get("fullName")
       username = data.get("username")
       email = data.get("email")
       password = data.get("password")

       if not full_name or not username or not email or not password:
          return jsonify({
                "Message": "fullName, username, email and password are required"
            }), 400

       location = data.get("location")
       phone_number = data.get("phone_number")

       img_link = None
       image_file = files.get("image")
       if image_file and image_file.filename:
          filename = secure_filename(image_file.filename)
          upload_folder = os.path.join(current_app.root_path, "static", "uploads", "students")
          os.makedirs(upload_folder, exist_ok=True)
          save_path = os.path.join(upload_folder, filename)
          image_file.save(save_path)
          img_link = f"/static/uploads/students/{filename}"

       user_data = {
            "account_id": account_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "roles": json.dumps(["ROLE_USER"]),
            "password": password,
            "phone": phone_number,
            "address": location,
            "status": 1,
            "enabled": 1,
       }
       if img_link:
          user_data["img_link"] = img_link

       filtered_data = {k: v for k, v in user_data.items() if v is not None}

       columns = ", ".join(filtered_data.keys())
       placeholders = ", ".join(["%s"] * len(filtered_data))
       values = list(filtered_data.values())

       query = f"INSERT INTO user ({columns}) VALUES ({placeholders})"
       result = Database.execute_query(query, values, fetch=False)

       if not result:
          return jsonify({"Message": "Student not created"}), 400


       session_change_groups = []
       if selected_sessions:
          placeholders_sessions = ", ".join(["%s"] * len(selected_sessions))
          query_relation = f"""
              SELECT id, max_group_change
              FROM session
              WHERE id IN({placeholders_sessions}) AND enabled = 1 AND account_id = %s
           """
          session_change_groups = Database.execute_query(
             query_relation,
             selected_sessions + [account_id],
             fetch=True
          )

          insert_relation_query = """
               INSERT INTO relation_user_session
                   (user_id, session_id, relation_group_local_session_id, ref, enabled, created_at, timestamp)
               VALUES
                   (%s, %s, %s, %s, %s, NOW(), NOW())
           """

          for session_row in session_change_groups:
             session_id = session_row["id"]
             try:
                max_group_change = int(session_row["max_group_change"])
             except (TypeError, ValueError):
                max_group_change = 0

             for _ in range(max_group_change):
                Database.execute_query(
                   insert_relation_query,
                   [result, session_id, None, None, 1],
                   fetch=False
                )

       # ── Create linked VirtualUser (mirrors remote createStudent) ────
       virtual_result = None
       existing_virtual = Database.execute_query(
          "SELECT id FROM virtual_user WHERE user_id = %s AND account_id = %s",
          (result, account_id),
          fetch=True
       )

       if not existing_virtual:
          virtual_uuid = str(uuid.uuid4())

          virtual_user_data = {
             "account_id": account_id,
             "user_id": result,
             "created_by_id": 0,  # TODO: replace with real admin user id if available
             "name": full_name,
             "phone": phone_number,
             "email": email,
             "status": 1,
             "enabled": 1,
             "uuid": virtual_uuid,
          }

          filtered_virtual_data = {k: v for k, v in virtual_user_data.items() if v is not None}

          v_columns = ", ".join(filtered_virtual_data.keys())
          v_placeholders = ", ".join(["%s"] * len(filtered_virtual_data))
          v_values = list(filtered_virtual_data.values())

          virtual_query = f"INSERT INTO virtual_user ({v_columns}) VALUES ({v_placeholders})"
          virtual_result = Database.execute_query(virtual_query, v_values, fetch=False)

          if not virtual_result:
             return jsonify({"Message": "Student created but virtual user not created"}), 400

          # ── Audit log for virtual_user creation ─────────────────
          virtual_audit_payload = dict(filtered_virtual_data)
          virtual_audit_payload["id"] = virtual_result

          virtual_audit_query = """
              INSERT INTO virtual_user_audit (action_type, record_id, old_data, new_data, is_synced)
              VALUES (%s, %s, %s, %s, %s)
          """
          Database.execute_query(
             virtual_audit_query,
             ["CREATE", virtual_result, None, json.dumps(virtual_audit_payload, default=str), 0],
             fetch=False
          )
       else:
          virtual_result = existing_virtual[0]["id"]

       # ── Audit log for user creation ──────────────────────────────────
       audit_payload = dict(filtered_data)
       audit_payload["id"] = result
       audit_payload["sessions"] = selected_sessions

       audit_query = """
           INSERT INTO user_audit (user_id, role, action_type, payload, is_synced)
           VALUES (%s, %s, %s, %s, %s)
       """
       Database.execute_query(
          audit_query,
          [result, "ROLE_USER", "CREATE", json.dumps(audit_payload, default=str), 0],
          fetch=False
       )

       return jsonify({
            "Message": "Student created successfully",
            "user_id": result,
            "virtual_user_id": virtual_result
        }), 200

    except Exception as e:
       return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# =============================================
# ENDPOINT 8: GET user in session
# =============================================
@users_bp.route('/get_students_with_sessions', methods=['GET'])
def get_student_with_session():
	try:
		query_get_student = """
			SELECT DISTINCT u.id,u.username,u.email
			FROM user u, relation_user_session rus,session s
			WHERE u.id = rus.user_id AND 
			u.enabled = 1 AND 
			rus.enabled = 1 AND rus.session_id = s.id
		"""
		result = Database.execute_query(query_get_student, fetch=True)

		if result:
			return jsonify({"Success": True, "data":result}),200
		else:
			return jsonify({"Success": False, "Data":[]}),200

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500


@users_bp.route('/associate-virtual-user/<int:account_id>', methods=['POST'])
def associate_virtual_user(account_id):
	try:
		data = request.get_json(silent=True) or request.form
		virtual_id = data.get('id')
		real_user_id = data.get('realUserId')

		if not virtual_id or not real_user_id:
			return jsonify({
				"Success": False,
				"Message": "Virtual or real user not found."
			}),400

		query_get_real_user = """
			SELECT user_id 
			FROM virtual_user
			WHERE id = %s AND enabled = 1 AND account_id = %s
		"""
		values =(virtual_id,account_id)
		real_user = Database.execute_query(query_get_real_user, values, fetch=True)[0]['user_id']
		print(real_user)
		if not real_user:
			return jsonify({
				"Message":f"There is no real_user for this virtual_user"
			}),404



		return jsonify(
			real_user
		),200


	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500