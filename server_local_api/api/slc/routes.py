from flask import Blueprint, jsonify
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# Create blueprint
slc_bp = Blueprint('slc', __name__, url_prefix='/scl')


# ========================================
# ROOM ENDPOINTS
# ========================================

# ENDPOINT 1: Get all rooms
@slc_bp.route('/get-all-room', methods=['GET'])
@token_required
def get_all_rooms():
    try:
        query = "SELECT * FROM room"
        rows = Database.execute_query(query)

        rooms = []
        for r in rows:
            rooms.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "capacity": str(r.get("capacity")) if r.get("capacity") else "0"
            })

        return jsonify({
            "success": True,
            "data": rooms
        }), 200

    except Exception as e:
        print(f"DEBUG: Error {e} coming from get_all_room_api")
        return jsonify({'message': 'Internal Server Error'}), 500


# ENDPOINT 2: Get local details by account
@slc_bp.route('/get_local_detail/<int:account_id>', methods=['GET'])
def get_local_detail(account_id):
    try:
        print(account_id)

        query = """
            SELECT 
                l.*,
                COALESCE(SUM(CAST(r.capacity AS UNSIGNED)), 0) as capacity
            FROM local l
            LEFT JOIN room r ON l.id = r.local_id AND r.enabled = 1
            WHERE l.account_id = %s AND l.enabled = 1
            GROUP BY l.id
        """
        results = Database.execute_query(query, (account_id,))

        if results:
            # Convert datetime objects to strings
            locals_data = []
            for row in results:
                local_data = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        local_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        local_data[key] = value
                locals_data.append(local_data)

            return jsonify({
                "success": True,
                "message": "Locals retrieved successfully",
                "data": locals_data,
                "count": len(locals_data)
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No locals found for this account",
                "data": []
            }), 404

    except Exception as e:
        print(f"DEBUG: Error {e} coming from get_local")
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


# ENDPOINT 3: Get rooms by local ID
@slc_bp.route('/get_room/<int:local_id>', methods=['GET'])
# @token_required
def get_rooms_by_local(local_id):
    try:
        query = """
            SELECT id, name, capacity 
            FROM room 
            WHERE local_id = %s AND enabled = 1
        """
        result = Database.execute_query(query, (local_id,))

        if result:
            return jsonify({
                "message": "Success",
                "data": result
            }), 200
        else:
            return jsonify({
                "message": "There is no room for this local"
            }), 404

    except Exception as e:
        print(f"Error {e} coming from get_room function")
        return jsonify({
            "message": f"Error {str(e)}"
        }), 500


@slc_bp.route('/get_slc_id',methods =['GET'])
def get_slc_id():
    try:
        query= """
            SELECT * FROM slc LIMIT 1;
        """
        result = Database.execute_query(query)
        if result:
            return jsonify({
                "Message":"Success",
                "data":result,
            }),200
        else:
            return jsonify({
                "Message":"Bad requests",
                "data":None
            }),404
    except Exception as e:
        return jsonify({"Message":f"Error: {e}"}),500