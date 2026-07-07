# app/account/routes.py
from http.client import responses
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app, Response
import io
import os
import base64
from app.account.services import (
	get_account_data_service,
	get_account_image_service,
	update_account_service


)

account_bp = Blueprint('account', __name__)



# ── GET account data ──────────────────────────────────────────────────────────
@account_bp.route('/api/get_account_data/<int:account_id>', methods=['GET'])
def get_account_data(account_id):
    try:
        status,response = get_account_data_service(account_id)
        if status:
            return jsonify(response.json()),response.status_code
        else:
            return jsonify({
                "Message":"Error in getting account_data"
            }),400
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500


# ── GET account image ──────────────────────────────────────────────────────────
@account_bp.route('/api/get_account_image/<int:account_id>', methods=['GET'])
def get_account_image(account_id):
    try:
        success, content, mimetype = get_account_image_service(account_id)

        if success and content:
            return Response(content, mimetype=mimetype)
        else:
            return jsonify({"Message": "Image not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({"Message": f"Error: {e} coming from server"}), 500

# ── UPDATE account ─────────────────────────────────────────────────────────────
@account_bp.route('/api/update_account/<int:account_id>', methods=['POST'])
def update_account(account_id):
    try:
        data_account = request.get_json(force=True)

        print(f"📋 Received data: {data_account}")
        print(f"📋 Account ID: {account_id}")

        if not data_account:
            return jsonify({"Message": "No data received"}), 400

        # ── Fix: account_id first, data second ────────────────
        status, response = update_account_service(account_id, data_account)

        if status:
            return jsonify({
                "Message": "Account updated with success",
                "Response": response
            }), 200
        else:
            print(f"❌ Service returned: {response}")
            return jsonify({
                "Message": "Error in updating account",
                "Response": response
            }), 400

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

