# app/account/routes.py
from http.client import responses
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app, Response
import io
import os
import base64
from app.teacher.services import (
	create_teacher_service,
	get_all_teacher_service
)

teacher_bp = Blueprint('teacher', __name__)



# ── CREATE teacher ──────────────────────────────────────────────────────────
@teacher_bp.route('/api/create_teacher', methods=['POST'])
def create_teacher():
    try:
        if not request.form:
            return jsonify({
                "Message": "There is no Data to create user"
            }), 400

        account_id = request.form.get("account_id")
        if not account_id:
            return jsonify({
                "Message": "account_id is required"
            }), 400

        form_items = [
            (k, v) for k, v in request.form.items(multi=True)
            if not k.endswith("[]") and k != "account_id"   # don't double-forward it
        ]

        for p in request.form.getlist("allowedPermissionAccess[]"):
            form_items.append(("allowedPermissionAccess[]", p))

        for s in request.form.getlist("allowedAccessSession[]"):
            form_items.append(("allowedAccessSession[]", s))

        status, response = create_teacher_service(int(account_id), form_items, request.files)

        if status:
            return jsonify({
                "Message": "success",
                "Response": response
            }), 200
        else:
            return jsonify({
                "Message": "Error",
                "Response": response
            }), 400

    except Exception as e:
        print(f"Error: {e} coming from create_teacher")
        return jsonify({
            "Message": f"Error: {e} coming from backend"
        }), 500


# ── GET teacher data ──────────────────────────────────────────────────────────
@teacher_bp.route('/api/get_teacher',methods=['GET'])
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
