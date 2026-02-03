from flask import Blueprint, request, jsonify
import jwt
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.auth import check_user, check_slc

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/scl')


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if check_user(username, password):
        token = jwt.encode(
            {"user": username},
            Config.SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route('/login_slc', methods=['POST'])
def login_slc():
    """Device (SLC) login endpoint"""
    data = request.get_json()
    mac = data.get("mac")
    password = data.get("password")

    if not mac or not password:
        return jsonify({"error": "MAC address and password required"}), 400

    if check_slc(mac, password):
        token = jwt.encode(
            {"user": mac},
            Config.SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200

    return jsonify({"error": "Invalid credentials"}), 401