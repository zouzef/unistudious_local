# app/user/routes.py
from http.client import responses

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
    delete_virtual_user,
    get_manager_info_service,
    get_user_info_service,
    create_user_service,
    get_all_teacher_service,
    create_teacher_service
)

user_bp = Blueprint('user', __name__)


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


#  ================================= BEGIN CRUD API USER =================================
@user_bp.route('/api/create-user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "Message": "No data to create user"
            }), 400

        status, response = create_user_service(data)

        if status:
            return jsonify({
                "Message": "User created with success"
            }), 200
        else:
            return jsonify({
                "Message": "User not created",
                "Details": response
            }), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from backend"
        }), 500


@user_bp.route('/api/update-user/<int:user_id>', methods=['POST'])
def api_update_user(user_id):
    """Update user"""
    try:
        data = request.get_json()
        success, message = update_user(user_id, data)
        if success:
            return jsonify({"Message": message}), 200
        else:
            return jsonify({"Message":message}),400
    except Exception as e:
        return jsonify({"Message": e}), 500


@user_bp.route('/api/delete-user/<int:user_id>', methods=['POST'])
def api_delete_user(user_id):
    """Delete user"""
    success, message = delete_user(user_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 404


@user_bp.route('/api/get-user-info/<int:user_id>', methods=['GET'])
def api_get_user_info(user_id):
    try:
        status, data = get_user_info_service(user_id)
        if status:
            return jsonify({"Data": data}), 200  # ✅ data is already a list
        else:
            return jsonify({"Message": "Failed to fetch data"}), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from backend"
        }), 500
#  ================================= END CRUD API USER =================================

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


@user_bp.route('/api/get-manager-info', methods=['GET'])
def get_manager_info():
    try:
        status, response = get_manager_info_service()
        if status:
            return jsonify(response), 200  # ✅ pass response directly
        else:
            return jsonify({"Message": "Failed to fetch data"}), 400
    except Exception as e:
        print(e)
        return jsonify({"Message": "Error coming from server"}), 500


@user_bp.route('/api/get_teacher',methods=['GET'])
def get_teacher():
    try:
        status,data = get_all_teacher_service()
        if status:
            return jsonify(data),200
        else:
            return jsonify(data),400

    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from the backend"
        }),500


@user_bp.route('/api/create_teacher',methods=['POST'])
def create_teacher():
    try:
        data = request.get_json()
        if not(data):
            return jsonify({
                "Message":"There is no Data to create user"
            })

        status,response = create_teacher_service(data)
        if status:
            return jsonify({
                "Message":"success",
                "Response":response
            }),200
        else:
            return jsonify({
                "Message":f"Error",
                "Response":response
            })
    except Exception as e:
        print(f"Error: {e} coming from create_teacher")
        return jsonify({
            "Message":f"Error: {e} coming from backend"
        })
