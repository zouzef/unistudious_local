# app/user/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
import io
import os
import base64
from app.user.service import (
    get_all_users,
    get_profile_image,
    update_user,
    delete_user,
    update_virtual_user,
    delete_virtual_user
)

user_bp = Blueprint('user', __name__)


# ==========================================
# PAGE ROUTES
# ==========================================

@user_bp.route('/dashboard/my-student')
def show_my_student():
    """Show my student page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id')
    return render_template('index.html',
                           page='my_student',
                           account_id=account_id)


@user_bp.route('/dashboard/platform_student')
def show_platform_student():
    """Show platform student page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id')
    return render_template('index.html',
                           page='platform_student',
                           account_id=account_id)


# ==========================================
# API ROUTES
# ==========================================

@user_bp.route('/api/get-all-users/<int:account_id>', methods=['GET'])
def api_get_all_users(account_id):
    """Get all users"""
    result = get_all_users(account_id)
    return jsonify({"Message": "Success", "data": result}), 200


@user_bp.route('/api/get_profile_img/<int:user_id>', methods=['GET'])
def api_get_profile_image(user_id):
    """Get profile image"""
    content, mimetype = get_profile_image(user_id)

    if content:
        return send_file(
            io.BytesIO(content),
            mimetype=mimetype,
            as_attachment=False
        )

    # Return default image
    try:
        default_img_path = os.path.join(
            current_app.root_path,
            '../static/assets/images/defult-admin.png'
        )
        return send_file(default_img_path, mimetype='image/png')
    except Exception:
        transparent_png = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        return send_file(io.BytesIO(transparent_png), mimetype='image/png')


@user_bp.route('/api/update-user/<int:user_id>', methods=['POST'])
def api_update_user(user_id):
    """Update user"""
    data = request.get_json()
    success, message = update_user(user_id, data)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 500


@user_bp.route('/api/delete-user/<int:user_id>', methods=['POST'])
def api_delete_user(user_id):
    """Delete user"""
    success, message = delete_user(user_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 404


@user_bp.route('/api/update-virtuel-user/<int:user_id>', methods=['POST'])
def api_update_virtual_user(user_id):
    """Update virtual user"""
    data = request.get_json()
    success, message = update_virtual_user(user_id, data)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 500


@user_bp.route('/api/delete-virtuel-user/<int:user_id>', methods=['POST'])
def api_delete_virtual_user(user_id):
    """Delete virtual user"""
    success, message = delete_virtual_user(user_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 404