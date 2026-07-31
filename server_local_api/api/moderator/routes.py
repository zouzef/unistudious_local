# server/moderator/routes.py  (LOCAL API SERVER)

import json
import bcrypt
import os
import sys
import time
import jwt
from flask import Blueprint, jsonify, request, current_app, send_file

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

moderator_bp = Blueprint('moderator', __name__, url_prefix='/scl')

REQUIRED_MODERATOR_ROLES = [
    'ROLE_MANAGER_ADMINISTRATIVE',
    'ROLE_MANAGER_CONFIG',
    'ROLE_MANAGER_FINANCE',
    'ROLE_MANAGER_HR',
    'ROLE_MANAGER_IT',
    'ROLE_MANAGER_MARKETING',
    'ROLE_CUSTOMER_MANAGER_SERVICE'
]


def _generate_token(user_id, username, account_id) -> str:
    """Issue a signed JWT directly from the local API server."""
    now = int(time.time())
    payload = {
        "sub":        str(user_id),
        "username":   username,
        "account_id": account_id,
        "iat":        now,
        "exp":        now + 3600,       # 1 hour — adjust in Config if needed
    }
    return jwt.encode(payload, str(Config.SECRET_KEY), algorithm="HS256")


# ============================================================
# ENDPOINT 1: Authenticate moderator
# ← NO @token_required — this IS the login, returns the JWT
# ============================================================
@moderator_bp.route('/authentification-moderateur', methods=['POST'])
def auth_moderator():
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()

        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not username:
            return jsonify({"message": "Username required"}), 400
        if not password:
            return jsonify({"message": "Password required"}), 400

        query = """
            SELECT
                u.id          AS user_id,
                u.password    AS password_hash,
                u.roles       AS roles,
                u.account_id  AS account_id
            FROM user u
            WHERE u.username = %s
              AND u.enabled  = 1
            LIMIT 1
        """
        result = Database.execute_query(query, (username,))

        if not result:
            return jsonify({"message": "Invalid credentials"}), 401

        row         = result[0]
        stored_hash = row['password_hash'].replace("$2y$", "$2b$")

        try:
            password_match = bcrypt.checkpw(
                password.encode("utf-8"),
                stored_hash.encode("utf-8")
            )
        except Exception:
            return jsonify({"message": "Invalid credentials"}), 401

        if not password_match:
            return jsonify({"message": "Invalid credentials"}), 401

        try:
            roles_data = json.loads(row['roles']) if row['roles'] else {}
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid roles format in database"}), 500

        user_roles    = list(roles_data.values()) if isinstance(roles_data, dict) else roles_data
        missing_roles = [r for r in REQUIRED_MODERATOR_ROLES if r not in user_roles]

        if missing_roles:
            return jsonify({
                "message":       "Insufficient permissions",
                "missing_roles": missing_roles
            }), 403

        # ── All checks passed → issue JWT ─────────────────────────────────────
        token = _generate_token(
            user_id    = row['user_id'],
            username   = username,
            account_id = row['account_id'],
        )

        return jsonify({
            "message":      "success",
            "user_id":      row['user_id'],
            "account_id":   row['account_id'],
            "access_token": token,          # ← JWT ready to copy into APIdog
            "token_type":   "Bearer",
        }), 200

    except Exception as e:
        print(f"[AUTH] Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================
# ENDPOINT 2: Moderator dashboard statistics
# ← protected
# ============================================================
@moderator_bp.route('/get_data_moderateur/<int:account_id>', methods=["GET"])
def get_data_moderateur(account_id):
    try:
        query = """
            SELECT
                (SELECT COUNT(*) FROM user
                 WHERE JSON_CONTAINS(roles, '"ROLE_USER"', '$')    AND enabled = 1) AS nbuser,
                (SELECT COUNT(*) FROM user
                 WHERE JSON_CONTAINS(roles, '"ROLE_TEACHER"', '$') AND enabled = 1) AS nbteach,
                (SELECT COUNT(*) FROM relation_group_local_session
                 WHERE enabled = 1) AS nbgroup,
                (SELECT COUNT(*) FROM session
                 WHERE enabled = 1) AS nbsession
        """
        result = Database.execute_query(query)
        return jsonify({
            'success': True,
            'data': {
                'nbuser':     result[0]['nbuser'],
                'nbteach':    result[0]['nbteach'],
                'nbgroup':    result[0]['nbgroup'],
                'nbsession':  result[0]['nbsession'],
                'account_id': account_id
            }
        }), 200

    except Exception as e:
        print(f"[DASHBOARD] Error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ============================================================
# ENDPOINT 3: Account data
# ← protected
# ============================================================
@moderator_bp.route('/get_account_data/<int:account_id>', methods=['GET'])
@token_required
def get_account_data(account_id):
    try:
        query = """
            SELECT name, file_link, status, created_at
            FROM account
            WHERE enabled = 1 AND id = %s
        """
        result = Database.execute_query(query, (account_id,), fetch=True)
        if result:
            return jsonify(result), 200
        return jsonify({"Message": "There is no data for this account_id"}), 404
    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ============================================================
# ENDPOINT 4: Account image
# ← protected
# ============================================================
@moderator_bp.route('/get_account_image/<int:account_id>', methods=['GET'])
@token_required
def get_account_image(account_id):
    try:
        query = """
            SELECT file_link FROM account
            WHERE enabled = 1 AND id = %s
        """
        result = Database.execute_query(query, (account_id,), fetch=True)

        if not result or not result[0].get('file_link'):
            return jsonify({"Message": "No image found for this account"}), 404

        file_link  = result[0]['file_link']
        image_path = os.path.join(
            current_app.root_path, 'uploads', 'academie_img',
            f'academie_{account_id}', file_link
        )

        if not os.path.exists(image_path):
            return jsonify({"Message": f"Image file not found: {image_path}"}), 404

        extension = file_link.rsplit('.', 1)[-1].lower()
        mimetype  = 'image/png' if extension == 'png' else 'image/jpeg'
        return send_file(image_path, mimetype=mimetype)

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500


# ============================================================
# ENDPOINT 5: Update account
# ← protected
# ============================================================
@moderator_bp.route('/update_account/<int:account_id>', methods=['POST'])
@token_required
def update_account(account_id):
    try:
        name   = request.form.get('name',   '').strip()
        status = request.form.get('status', '').strip()
        logo   = request.files.get('logoFile')

        if not name:
            return jsonify({"Message": "Name is required"}), 400
        if status not in ('0', '1'):
            return jsonify({"Message": "Status must be 0 or 1"}), 400

        new_file_link = None
        if logo and logo.filename:
            if not allowed_file(logo.filename):
                return jsonify({"Message": "Only PNG, JPG, and JPEG files are allowed"}), 400
            upload_dir = os.path.join(
                current_app.root_path, 'uploads', 'academie_img',
                f'academie_{account_id}'
            )
            os.makedirs(upload_dir, exist_ok=True)
            from werkzeug.utils import secure_filename
            filename      = secure_filename(logo.filename)
            save_path     = os.path.join(upload_dir, filename)
            logo.save(save_path)
            new_file_link = filename

        if new_file_link:
            query  = "UPDATE account SET name=%s, status=%s, file_link=%s WHERE enabled=1 AND id=%s"
            params = (name, int(status), new_file_link, account_id)
        else:
            query  = "UPDATE account SET name=%s, status=%s WHERE enabled=1 AND id=%s"
            params = (name, int(status), account_id)

        rows_affected = Database.execute_query(query, params, fetch=False)
        if rows_affected == 0:
            return jsonify({"Message": "Account not found or nothing changed"}), 404
        return jsonify({"Message": "Account updated successfully"}), 200

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500