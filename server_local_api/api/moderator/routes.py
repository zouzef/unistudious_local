from flask import Blueprint, jsonify, request
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
            SELECT roles FROM user WHERE username = %s AND enabled = 1
        """
        result = Database.execute_query(query, (username,))

        if not result:
            return jsonify({"message": "User Not Found"}), 404

        # Parse the JSON roles field
        roles_data = json.loads(result[0]['roles']) if result[0]['roles'] else {}

        # Extract role values (since it's stored as a dict with numeric keys)
        if isinstance(roles_data, dict):
            user_roles = list(roles_data.values())
        else:
            user_roles = roles_data

        # Check if user has ALL required moderator roles
        has_all_roles = all(role in user_roles for role in REQUIRED_MODERATOR_ROLES)

        if has_all_roles:
            return jsonify({"message": "success"}), 200
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
