from flask import Blueprint, jsonify,request
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


# ENDPOINT 4: Create Camera
@devices_bp.route('/create_camera', methods=['POST'])
def create_camera():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "Message": "There is no data to create camera"
            }), 400

        required_fields = ['slc_id', 'room_id', 'name', 'mac_id', 'username', 'password', 'type', 'status']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            return jsonify({
                "Message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        slc_id      = data.get('slc_id')
        room_id     = data.get('room_id')
        name        = data.get('name')
        mac_id      = data.get('mac_id')
        username    = data.get('username')
        password    = data.get('password')
        cam_type    = data.get('type')   # renamed to avoid shadowing built-in
        status      = data.get('status')

        query = """
            INSERT INTO camera 
            (slc_id, room_id, name, mac_id, username, password, type, status, enabled, timestamp, created_at,slc_edit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(),1)
        """
        values = (slc_id, room_id, name, mac_id, username, password, cam_type, status, 1)
        result = Database.execute_query(query, values, fetch=False)

        if result:
            return jsonify({
                "Message": "Camera created successfully"
            }), 200
        else:
            return jsonify({
                "Message": "Failed to create camera"
            }), 400

    except Exception as e:
        print(e)
        return jsonify({

            "Message": f"Error: {e} coming from server"
        }), 500


# ENDPOINT 5: DELETE Camera
@devices_bp.route('/delete_camera/<int:camera_id>',methods=['POST'])
def delete_camera(camera_id):
    try:
        query = """
            SELECT count(*) AS nbr
            FROM camera 
            WHERE id = %s AND enabled = 1
        """
        values =(camera_id,)
        result = Database.execute_query(query, values,fetch=True)[0]['nbr']
        if result == 0:
            return jsonify({
                "Message":f"There is no camra with this id"
            }),404
        else:
            query = """
                UPDATE camera
                set enabled = 0 AND slc_edit = 1
                WHERE id = %s 
            """
            values=(camera_id,)
            result = Database.execute_query(query, values,fetch=False)
            if result:
                return jsonify({
                    "Message":f"Camera Deleted with Success"
                }),200
            else:
                return jsonify({
                    "Message":f"Camera dosent deleted "
                }),400
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        })


# ENDPOINT 6: Update Camera
@devices_bp.route('/update_camera/<int:camera_id>', methods=['POST'])
def update_camera(camera_id):
    try:
        data = request.get_json()

        # Check if camera exists
        query = """
            SELECT count(*) as nbr 
            FROM camera 
            WHERE id = %s
        """
        values = (camera_id,)
        result = Database.execute_query(query, values, fetch=True)

        if result[0]['nbr'] == 0:
            return jsonify({
                "Message": "There is no camera with this id"
            }), 404

        # Build dynamic update query based on provided fields
        allowed_fields = {
            "type": "type",
            "name": "name",
            "mac_id": "mac_id"
        }

        fields_to_update = []
        values_to_update = []

        for key, column in allowed_fields.items():
            if key in data:
                fields_to_update.append(f"{column} = %s")
                values_to_update.append(data[key])

        if not fields_to_update:
            return jsonify({
                "Message": "No valid fields provided to update"
            }), 400

        values_to_update.append(camera_id)

        query = f"""
            UPDATE camera
            SET {', '.join(fields_to_update)}
            WHERE id = %s
        """

        Database.execute_query(query, tuple(values_to_update), fetch=False)

        return jsonify({
            "Message": "Camera updated successfully"
        }), 200

    except Exception as e:
        print(e)
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# ========================================
# TABLET ENDPOINTS
# ========================================

# ENDPOINT 1: Create tablet
@devices_bp.route('/create_tablet', methods=['POST'])
def create_tablet():
    try:
        data = request.get_json()
        required_fields = ['name', 'mac_id', 'password','slc_id','room_id']

        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        if missing_fields:
            return jsonify({
                "Message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        query = """
            INSERT INTO tablet (slc_id, room_id, name, mac_id, password,enabled,created_at)
            VALUES (%s, %s, %s, %s, %s,1)
        """
        values = (
            data.get('slc_id', None),
            data.get('room_id', None),
            data['name'],
            data['mac_id'],
            data['password']
        )

        Database.execute_query(query, values, fetch=False)

        return jsonify({
            "Message": "Tablet created successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

# ENDPOINT 1: Get all tablets
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



# ENDPOINT 2: Get all tablets by room
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



# ENDPOINT 3: Get tablet by ID
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
