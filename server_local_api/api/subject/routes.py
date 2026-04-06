from flask import Blueprint, jsonify, request  # ← only one import line
import sys
import os
import json
from datetime import datetime, timedelta
import bcrypt
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


subject_bp = Blueprint('subjects', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Get all sub_subject
# ========================================
@subject_bp.route('/get_sub_subjects', methods=['GET'])  # ← fixed
def get_subjects():
    try:
        query = """
            SELECT 
                a.subject_config_id,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE sc.name
                END AS subject_identifier
            FROM account_subject a
            LEFT JOIN subject_config sc ON sc.id = a.subject_config_id
        """
        result = Database.execute_query(query,fetch=True)
        return jsonify({
            "Message":"Success",
            "data":result
        }),200
    except Exception as e:
        print(f"Error coming from the get_subject: {e}")
        return jsonify({
            "Message": f"Error: {e} coming from the server"
        }), 500