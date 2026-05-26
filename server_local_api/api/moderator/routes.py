from flask import Blueprint, jsonify, request, current_app, send_file
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database

# Create blueprint
moderator_bp = Blueprint('moderator', __name__, url_prefix='/scl')

# Required moderator roles
REQUIRED_MODERATOR_ROLES = [
    'ROLE_MANAGER_ADMINISTRATIVE',
    'ROLE_MANAGER_CONFIG',
    'ROLE_MANAGER_FINANCE',
    'ROLE_MANAGER_HR',
    'ROLE_MANAGER_IT',
    'ROLE_MANAGER_MARKETING',
    'ROLE_CUSTOMER_MANAGER_SERVICE'
]


# ========================================
# ENDPOINT 1: Authenticate moderator
# ========================================
@moderator_bp.route('/authentification-moderateur', methods=['POST'])
def auth_moderator():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Validate required fields
        if 'username' not in data:
            return jsonify({"message": "Username required"}), 400

        username = data['username']

        # Fetch user with roles
        query = """
            SELECT id,roles FROM user WHERE username = %s AND enabled = 1
        """
        result = Database.execute_query(query, (username,))

        if not result:
            return jsonify({"message": "User Not Found"}), 404

        # Parse the JSON roles field
        roles_data = json.loads(result[0]['roles']) if result[0]['roles'] else {}
        user_id = result[0]['id']

        # Extract role values (since it's stored as a dict with numeric keys)
        if isinstance(roles_data, dict):
            user_roles = list(roles_data.values())
        else:
            user_roles = roles_data

        # Check if user has ALL required moderator roles
        has_all_roles = all(role in user_roles for role in REQUIRED_MODERATOR_ROLES)

        if has_all_roles:
            return jsonify({
                "message": "success",
                "user_id": user_id,
            }), 200
        else:
            missing_roles = [role for role in REQUIRED_MODERATOR_ROLES if role not in user_roles]
            print(f"DEBUG: Missing roles: {missing_roles}")
            return jsonify({
                "message": "Insufficient permissions",
                "missing_roles": missing_roles
            }), 403

    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON decode error {e}")
        return jsonify({"error": "Invalid roles format"}), 500

    except Exception as e:
        print(f"DEBUG: Error {e} coming from auth moderator")
        return jsonify({"error": "Internal server error"}), 500


# ========================================
# ENDPOINT 2: Get moderator dashboard statistics
# ========================================
@moderator_bp.route('/get_data_moderateur/<int:account_id>', methods=["GET"])
def get_data_moderateur(account_id):
    """
    Get statistics for moderator dashboard

    Returns:
        - nbuser: Count of users with ROLE_USER
        - nbteach: Count of teachers with ROLE_TEACHER
        - nbgroup: Count of active groups
        - nbsession: Count of active sessions
    """
    try:
        # Get all counts in one query
        query = """
            SELECT 
                (SELECT COUNT(*) FROM user 
                 WHERE JSON_CONTAINS(roles, '"ROLE_USER"', '$') AND enabled = 1) as nbuser,
                (SELECT COUNT(*) FROM user 
                 WHERE JSON_CONTAINS(roles, '"ROLE_TEACHER"', '$') AND enabled = 1) as nbteach,
                (SELECT COUNT(*) FROM relation_group_local_session 
                 WHERE enabled = 1) as nbgroup,
                (SELECT COUNT(*) FROM session 
                 WHERE enabled = 1) as nbsession
        """
        result = Database.execute_query(query)

        return jsonify({
            'success': True,
            'data': {
                'nbuser': result[0]['nbuser'],
                'nbteach': result[0]['nbteach'],
                'nbgroup': result[0]['nbgroup'],
                'nbsession': result[0]['nbsession'],
                'account_id': account_id
            }
        }), 200

    except Exception as e:
        print(f"Error in get_data_moderateur: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# =========================== ACCOUNT ===============
@moderator_bp.route('/get_account_data/<int:account_id>', methods=['GET'])
def get_account_data(account_id):
    try:
        query = """
            SELECT 
                name,
                file_link,
                status,
                created_at
            FROM account
            WHERE enabled = 1 and id = %s
        """
        result = Database.execute_query(query,(account_id,),fetch=True)
        if result:
            return jsonify(result),200
        else:
            return jsonify({"Message":"There is no data for this account_id"}),404
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500

# ── GET account image ──────────────────────────────────────────────────────────
@moderator_bp.route('/get_account_image/<int:account_id>', methods=['GET'])
def get_account_image(account_id):
    try:
        query = """
            SELECT file_link
            FROM account
            WHERE enabled = 1 AND id = %s
        """
        result = Database.execute_query(query, (account_id,), fetch=True)

        if not result or not result[0].get('file_link'):
            return jsonify({"Message": "No image found for this account"}), 404

        file_link  = result[0]['file_link']
        image_path = os.path.join(
            current_app.root_path,
            'uploads',
            'academie_img',
            f'academie_{account_id}',   # e.g. academie_3
            file_link                   # e.g. screenshot-20240923-103624-....jpg
        )

        if not os.path.exists(image_path):
            return jsonify({"Message": f"Image file not found: {image_path}"}), 404

        extension = file_link.rsplit('.', 1)[-1].lower()
        mimetype  = 'image/png' if extension == 'png' else 'image/jpeg'

        return send_file(image_path, mimetype=mimetype)

    except Exception as e:
        print(e)
        return jsonify({"Message": f"Error: {e} coming from server"}), 500

# ── UPDATE account ─────────────────────────────────────────────────────────────
@moderator_bp.route('/update_account/<int:account_id>', methods=['POST'])
def update_account(account_id):
    try:
        name   = request.form.get('name',   '').strip()
        status = request.form.get('status', '').strip()
        logo   = request.files.get('logoFile')

        if not name:
            return jsonify({"Message": "Name is required"}), 400

        if status not in ('0', '1'):
            return jsonify({"Message": "Status must be 0 or 1"}), 400

        # ── Handle logo upload (optional) ──────────────────────
        new_file_link = None

        if logo and logo.filename:
            if not allowed_file(logo.filename):
                return jsonify({"Message": "Only PNG, JPG, and JPEG files are allowed"}), 400

            # Mirror the exact folder structure: uploads/academie_img/academie_{id}/
            upload_dir = os.path.join(
                current_app.root_path,
                'uploads',
                'academie_img',
                f'academie_{account_id}'
            )
            os.makedirs(upload_dir, exist_ok=True)

            filename      = secure_filename(logo.filename)
            save_path     = os.path.join(upload_dir, filename)
            logo.save(save_path)
            new_file_link = filename

        # ── Build query dynamically ────────────────────────────
        if new_file_link:
            query  = """
                UPDATE account
                SET name = %s, status = %s, file_link = %s
                WHERE enabled = 1 AND id = %s
            """
            params = (name, int(status), new_file_link, account_id)
        else:
            query  = """
                UPDATE account
                SET name = %s, status = %s
                WHERE enabled = 1 AND id = %s
            """
            params = (name, int(status), account_id)

        rows_affected = Database.execute_query(query, params, fetch=False)

        if rows_affected == 0:
            return jsonify({"Message": "Account not found or nothing changed"}), 404

        return jsonify({"Message": "Account updated successfully"}), 200

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500