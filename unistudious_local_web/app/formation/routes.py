from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.formation.service import (
	fetch_formation_info
)

formation_bp = Blueprint('formation', __name__)

@formation_bp.route('/api/get-formation-info/<int:account_id>', methods=['GET'])
def get_formation_info(account_id):
    try:
        status, formation_info = fetch_formation_info(account_id)
        if status and formation_info:
            return jsonify(formation_info), 200  # ← fixed
        else:
            return jsonify({"Message": "Error"}), 404
    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from get_formation_info"}), 500