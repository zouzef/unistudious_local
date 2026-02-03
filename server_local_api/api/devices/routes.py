from flask import Blueprint, jsonify
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# Create blueprint
devices_bp = Blueprint('devices', __name__, url_prefix='/scl')


# ========================================
# CAMERA ENDPOINTS
# ========================================

# ENDPOINT 1: Get all cameras
@devices_bp.route('/get-all-camera', methods=['GET'])
# @token_required
def get_all_cameras():
    try:
        query = "SELECT * FROM camera"
        rows = Database.execute_query(query)

        cameras = []
        for row in rows:
            cameras.append({
                "id": row["id"],
                "type": row["type"],
                "name": row["name"],
                "mac": row["mac_id"],
                "username": row.get("username") or "",
                "password": row.get("password") or "",
                "status": "Active" if row.get("enabled", 1) else "Inactive",
                "roomId": row.get("room_id"),
                "roomName": row.get("room_name"),
                "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S") if row.get("created_at") else None
            })

        return jsonify(cameras), 200

    except Exception as e:
        print(f"DEBUG: Error {e} coming from get_all_camera_api")
        return jsonify({'message': 'Internal Server Error'}), 500


# ENDPOINT 2: Get all cameras by room
@devices_bp.route('/get-all-camera-room/<int:room_id>', methods=['GET'])
# @token_required
def get_all_cameras_by_room(room_id):
    try:
        query = "SELECT * FROM camera WHERE room_id = %s"
        rows = Database.execute_query(query, (room_id,))

        cameras = []
        for row in rows:
            cameras.append({
                "id": row["id"],
                "type": row["type"],
                "name": row["name"],
                "mac": row["mac_id"],
                "username": row.get("username") or "",
                "password": row.get("password") or "",
                "status": "Active" if row.get("enabled", 1) else "Inactive",
                "roomId": row.get("room_id"),
                "roomName": row.get("room_name"),
                "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S") if row.get("created_at") else None
            })

        return jsonify(cameras), 200

    except Exception as e:
        print(f"DEBUG: Error {e} coming from get_all_camera_by_room")
        return jsonify({'message': 'Internal Server Error'}), 500

# ENDPOINT 3: Get camera by ID
@devices_bp.route('/view-camera/<int:camera_id>', methods=['GET'])
# @token_required
def view_camera_by_id(camera_id):
    try:
        # Fetch camera with the room name using JOIN
        query = """
            SELECT c.id, c.type, c.name, c.mac_id, c.username, c.password, c.status, 
                   c.room_id AS roomId, r.name AS roomName, c.created_at
            FROM camera c
            LEFT JOIN room r ON c.room_id = r.id
            WHERE c.id = %s
        """
        camera = Database.execute_query(query, (camera_id,))

        if not camera:
            return jsonify({"success": False, "message": "Camera not found"}), 404

        return jsonify({
            "success": True,
            "camera": camera[0]
        }), 200

    except Exception as e:
        print(f"DEBUG: Error {e} coming from view_camera_by_id")
        return jsonify({'message': 'Internal Server Error'}), 500

# ========================================
# TABLET ENDPOINTS
# ========================================

# ENDPOINT 4: Get all tablets
@devices_bp.route('/get-all-tablets', methods=['GET'])
# @token_required
def get_all_tablets():
    try:
        query = """
            SELECT 
                id,
                name,
                mac_id as mac,
                password,
                status,
                room_id as roomId
            FROM tablet
        """
        rows = Database.execute_query(query)

        # Transform the data to match the desired format
        formatted_data = []
        for row in rows:
            formatted_data.append({
                "id": row["id"],
                "name": row["name"],
                "mac": row["mac"],
                "password": row["password"],
                "status": row["status"],
                "roomId": row["roomId"],
                "roomName": f"Room {row['roomId']}" if row["roomId"] else "No Room Assigned"
            })

        return jsonify(formatted_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



# ENDPOINT 5: Get all tablets by room
@devices_bp.route('/get-all-tablet-room/<int:room_id>', methods=['GET'])
# @token_required
def get_tablets_by_room(room_id):
    try:
        query = """
            SELECT 
                id,
                name,
                mac_id as mac,
                password,
                status,
                room_id as roomId
            FROM tablet 
            WHERE room_id = %s
        """
        rows = Database.execute_query(query, (room_id,))

        # Transform the data to match the desired format
        formatted_data = []
        for row in rows:
            formatted_data.append({
                "id": row["id"],
                "name": row["name"],
                "mac": row["mac"],
                "password": row["password"],
                "status": row["status"],
                "roomId": row["roomId"],
                "roomName": f"Room {row['roomId']}" if row["roomId"] else "No Room Assigned"
            })

        return jsonify(formatted_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



# ENDPOINT 6: Get tablet by ID
@devices_bp.route('/view-tablet/<int:id_tablette>', methods=['GET'])
# @token_required
def view_tablet_by_id(id_tablette):
    try:
        query = "SELECT * FROM tablet WHERE id = %s"
        rows = Database.execute_query(query, (id_tablette,))

        if not rows:
            return jsonify({
                "status": "error",
                "message": "Tablet not found"
            }), 404

        # Transform the data to match the desired format
        formatted_data = []
        for row in rows:
            formatted_data.append({
                "id": row["id"],
                "name": row["name"],
                "mac": row["mac_id"],
                "password": row["password"],
                "status": row["status"],
                "roomId": row["room_id"]
            })

        return jsonify(formatted_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500