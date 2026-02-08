from flask import Blueprint, jsonify, request
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# Create blueprint
sessions_bp = Blueprint('sessions', __name__, url_prefix='/scl')


# ========================================
# SESSION ENDPOINTS
# ========================================

# ENDPOINT 1: Get session details by account
@sessions_bp.route('/get_session_detail/<int:account_id>', methods=['GET'])
def get_session_detail(account_id):
    try:
        query = """
            SELECT 
                s.id, 
                s.account_id, 
                s.formation_id, 
                s.name as session_name, 
                s.description, 
                s.status, 
                s.img_link, 
                s.start_date, 
                s.end_date, 
                s.capacity, 
                s.price, 
                s.currency, 
                s.type_pay, 
                s.request_change_group, 
                s.max_group_change, 
                s.payment_methode, 
                s.number_session_for_pay, 
                s.price_student_absent, 
                s.user_register_after_start, 
                s.public_resource, 
                s.enabled, 
                s.created_at, 
                s.timestamp, 
                s.updated_at, 
                s.uuid, 
                s.price_presence, 
                s.price_online, 
                s.special_group, 
                s.passage, 
                s.season_id, 
                s.releaseToken, 
                s.useToken, 
                s.slc_use,
                f.name as formation_name
            FROM session as s
            INNER JOIN formation as f ON f.id = s.formation_id
            WHERE s.account_id = %s AND s.enabled = 1
        """
        results = Database.execute_query(query, (account_id,))

        if results:
            sessions = []
            for row in results:
                # Convert status integer to string for display
                status_value = row['status']

                if isinstance(status_value, int):
                    status_text = "Active" if status_value == 1 else "Inactive"
                    status_class = "badge-success" if status_value == 1 else "badge-danger"
                else:
                    status_text = status_value
                    status_class = "badge-success" if str(status_value).lower() == 'active' else "badge-danger"

                # Build session data with all attributes
                session_data = {
                    "id": row['id'],
                    "account_id": row['account_id'],
                    "formation_id": row['formation_id'],
                    "name": row['session_name'],
                    "description": row['description'],
                    "formation": row['formation_name'],
                    "status": status_text,
                    "status_class": status_class,
                    "status_raw": row['status'],
                    "img_link": row['img_link'],
                    "image_url": row['img_link'],
                    "start_date": row['start_date'].strftime('%Y-%m-%d') if row['start_date'] else None,
                    "end_date": row['end_date'].strftime('%Y-%m-%d') if row['end_date'] else None,
                    "capacity": row['capacity'],
                    "price": row['price'],
                    "currency": row['currency'],
                    "type_pay": row['type_pay'],
                    "request_change_group": row['request_change_group'],
                    "max_group_change": row['max_group_change'],
                    "payment_methode": row['payment_methode'],
                    "number_session_for_pay": row['number_session_for_pay'],
                    "price_student_absent": row['price_student_absent'],
                    "user_register_after_start": row['user_register_after_start'],
                    "public_resource": row['public_resource'],
                    "enabled": row['enabled'],
                    "created_at": row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else None,
                    "timestamp": row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if row['timestamp'] else None,
                    "updated_at": row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else None,
                    "uuid": row['uuid'],
                    "price_presence": row['price_presence'],
                    "price_online": row['price_online'],
                    "special_group": row['special_group'],
                    "passage": row['passage'],
                    "season_id": row['season_id'],
                    "releaseToken": row['releaseToken'],
                    "useToken": row['useToken'],
                    "slc_use": row['slc_use']
                }
                sessions.append(session_data)

            return jsonify({
                "success": True,
                "data": sessions,
                "count": len(sessions)
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No sessions found for this account",
                "data": []
            }), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500



