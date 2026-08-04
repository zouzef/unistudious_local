# app/account/routes.py
from http.client import responses
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app, Response
import io
import os
import base64
from app.manager.services import (
	get_manager_info_service,
	create_manager_service,
	update_manager_service,
	delete_manager_service

)

manager_bp = Blueprint('manager',__name__)

# ── GET manager info ───────────────────────────────────────────────────────────
@manager_bp.route('/api/get-manager-info', methods=['GET'])
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


# ── Create Manager ─────────────────────────────────────────────────────────────
@manager_bp.route('/api/create_manager/<int:account_id>', methods=['POST'])
def create_manager(account_id):
    try:
        if not request.form:
            return jsonify({
                "Message": "There is no Data to create user"
            }), 400

        form_items = [
            (k, v) for k, v in request.form.items(multi=True)
            if not k.endswith("[]")
        ]

        for r in request.form.getlist("roles[]"):
            form_items.append(("roles[]", r))

        status, response = create_manager_service(account_id, form_items, request.files)

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
        print(e)
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# ── Update Manager ─────────────────────────────────────────────────────────────
@manager_bp.route('/api/update-manager/<int:manager_id>', methods=['POST'])
def update_manager(manager_id):
	try:
		if not request.form:
			return jsonify({
				"Message": "There is no Data to update user"
			}), 400

		form_items = [
			(k, v) for k, v in request.form.items(multi=True)
			if not k.endswith("[]")
		]

		for r in request.form.getlist("roles[]"):
			form_items.append(("roles[]", r))

		status, response = update_manager_service(manager_id, form_items, request.files)

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
		print(e)
		return jsonify({
			"Message": f"Error: {e} coming from server"
		}), 500


@manager_bp.route('/api/delete-user/<int:manager_id>', methods=['POST'])
def delete_manager(manager_id):
	try:
		status, response = delete_manager_service(manager_id)
		if status:
			return jsonify(response.json()), 200
		else:
			return jsonify({"Message": "Failed to fetch data"}), 400

	except Exception as e:
		return jsonify({
			"Message": f"Error {e} coming from backend"
		}), 500