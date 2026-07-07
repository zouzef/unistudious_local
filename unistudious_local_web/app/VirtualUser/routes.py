# app/VirtualUser/routes.py
from http.client import responses

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app, Response
import io
import os
import base64
from app.VirtualUser.services import (
	create_virtuel_user_service,
	update_virtual_student,
	delete_virtual_user_service,
)


Virtual_user = Blueprint('virtual_user', __name__)


# ── Create Virtuel Student ─────────────────────────────────────────────────────────────
@Virtual_user.route('/api/create_virtuel_user', methods=['POST'])
def create_virtuel_user():
    try:
        if not request.form:
            return jsonify({"Message": "There is no Data to create virtueluser"}), 400

        account_id = request.form.get("account_id")
        if not account_id:
            return jsonify({"Message": "account_id is required"}), 400

        full_name = request.form.get("fullName")
        email = request.form.get("email")

        if not full_name or not email:
            return jsonify({"Message": "fullName and email are required"}), 400

        form_data = {
            "fullName": full_name,
            "email": email,
            "phone": request.form.get("phone"),
            "status": request.form.get("status", 1)
        }

        status, response = create_virtuel_user_service(int(account_id), form_data)

        if status:
            return jsonify(response), 200
        else:
            return jsonify(response or {"Message": "Failed to create virtual user"}), 400

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from server"}), 500

# ── Update Virtuel Student ─────────────────────────────────────────────────────────────
@Virtual_user.route('/api/update-virtual-student', methods=['POST'])
def api_update_virtual_student():
    """Update (or create) a virtual student"""
    try:
        data = request.get_json()

        vu_id   = data.get('id')
        user_id = data.get('userId')
        account_id = data.get('accountId')

        if not vu_id or not user_id:
            return jsonify({"Message": "id and userId are required"}), 400

        success, result = update_virtual_student(vu_id, user_id, data,account_id)

        if success:
            return jsonify({"Message": "Virtual student updated successfully", "student": result}), 200
        else:
            return jsonify({"Message": result}), 400
    except Exception as e:
        print(e)
        return jsonify({"Message": str(e)}), 500

# ── Delete Student ─────────────────────────────────────────────────────────────
@Virtual_user.route('/api/delete-virtuel-user/<int:user_id>', methods=['POST'])
def api_delete_virtual_user(user_id):
    """Delete virtual user"""
    data = request.get_json(silent=True) or {}
    account_id = data.get('account_id')
    virtual_id = data.get('id')

    if not account_id or not virtual_id:
        return jsonify({"Message": "account_id and id are required"}), 400

    success, message = delete_virtual_user_service(user_id, account_id, virtual_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 404