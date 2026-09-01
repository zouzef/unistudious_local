# app/user/routes.py
from http.client import responses

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app, Response
import io
import os
import base64
from app.user.service import (
    get_all_users,
    get_profile_image,
    update_user,
    get_user_info_service,
    create_student_service,
    get_student_with_session_service,
    associate_virtuel_user_service,
    get_all_real_user_service,
    get_user_registration_service,
    get_history_attendance_service
)

user_bp = Blueprint('user', __name__)


# ── GET List Student  ──────────────────────────────────────────────────────────
@user_bp.route('/api/get-all-users/<int:account_id>', methods=['GET'])
def api_get_all_users(account_id):
    """Get all users"""
    result = get_all_users(account_id)
    return jsonify({"Message": "Success", "data": result}), 200


# ── GET Profile Image Student  ──────────────────────────────────────────────────────────
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


# ── GET Student Info  ──────────────────────────────────────────────────────────
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


# ── Create Student ─────────────────────────────────────────────────────────────
@user_bp.route('/api/create_student/<int:account_id>',methods=['POST'])
def create_student(account_id):
    try:
        if not request.form:
            return jsonify({
                "Message":"There is no Data to create user"
            }),400
        form_items = list(request.form.items())

        status, response = create_student_service(account_id, form_items, request.files)

        if status:
            return jsonify({
                "Message": "success",
                "Response": response
            }),200
        else:
            return jsonify({
                "Message": "Error",
                "Response": response
            }),400
    except Exception as e:
        print(e)
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500


# ── GET Student Associated To Session  ──────────────────────────────────────────────────────────
@user_bp.route('/api/get_students_with_sessions', methods=['GET'])
def get_student_with_session():
    try:
        success, response = get_student_with_session_service()
        if success:
            return jsonify(response), 200  # <-- fixed typo, response is just data (a list), not a Flask response
        else:
            return jsonify(response), 400  # adjust status code to whatever makes sense for your failure case
    except Exception as e:
        print(e)
        return jsonify({
            "Message": f"Error: {e} coming from backend"
        }), 500

# ── Associate VirtuelUser To User ──────────────────────────────────────────────────────────
@user_bp.route('/api/associate_virtueluser/<int:account_id>', methods=['POST'])
def associate_virtuel_user(account_id):
    try:
        data = request.get_json()
        virtuel_id = data.get('id')
        real_user_id = data.get('realUserId')

        if not virtuel_id or not real_user_id:
            return jsonify({
                "success": False,
                "message": "Virtuel or real user not found."
            }), 400

        success, response = associate_virtuel_user_service(account_id, data)

        # response is a `requests.Response` (from calling the remote Symfony API),
        # not a flask.Response — convert it manually
        try:
            body = response.json()
        except ValueError:
            body = {"message": response.text}

        return jsonify(body), response.status_code

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

# ── GET Real Student  ──────────────────────────────────────────────────────────
@user_bp.route('/api/get-real-user', methods=['GET'])
def get_real_user():
    try:
        success, response = get_all_real_user_service()

        if success:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        print(e)
        return jsonify({
            "Message":f"Error: {e} in backend"
        }),500

# ── GET student registration  ──────────────────────────────────────────────────────────
@user_bp.route('/api/get-user-registration', methods=['GET'])
def get_user_registration():
    try:
        status, response = get_user_registration_service()
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from backend"}), 500

# ── GET student registration  ──────────────────────────────────────────────────────────
@user_bp.route('/api/get-user-history/<int:session_id>/<int:user_id>')
def get_history_attendance(session_id, user_id):
    try:
        status_ok, response = get_history_attendance_service(session_id, user_id)
        print(response)
        if status_ok:
            return jsonify(response.json()), 200
        else:
            return jsonify({"Message": "Failed to fetch attendance history"}), 500

    except Exception as e:
        print(e)
        return jsonify({"Message": f"Error: {e} coming from backend"}),500
