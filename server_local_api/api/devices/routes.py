from flask import Blueprint, jsonify,request
from datetime import datetime
import sys
import os



# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required
from util.audit import log_audit

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
        query = """
            SELECT c.*,r.name as roomName
                FROM camera c,room r
                WHERE r.id = c.room_id AND r.enabled = 1 AND c.enabled = 1
         """
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
                "roomName": row.get("roomName"),
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
        query = "SELECT * FROM camera WHERE room_id = %s AND enabled = 1"
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
        print(data)
        if not data:
            return jsonify({
                "Message": "There is no data to create camera"
            }), 400

        required_fields = ['slc_id', 'room_id', 'name', 'mac_id', 'type', 'status']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            return jsonify({
                "Message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # username & password are required only for IP cameras
        if data.get('type') == 'ipcam':
            ip_required = ['username', 'password']
            ip_missing = [field for field in ip_required if field not in data or not data[field]]

            if ip_missing:
                return jsonify({
                    "Message": f"Missing required fields for IP camera: {', '.join(ip_missing)}"
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
            (slc_id, room_id, name, mac_id, username, password, type, status, enabled, timestamp, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        values = (slc_id, room_id, name, mac_id, username, password, cam_type, status, 1)
        result = Database.execute_query(query, values, fetch=False)
        if result:
            inserted_id = result
            new_record = Database.execute_query(
                "SELECT * FROM camera WHERE id = %s",
                (inserted_id,),
                fetch=True
            )
            new_rec = new_record[0] if new_record else None
            log_audit(
                table_name="camera_audit",
                action_type="INSERT",
                old_data=None,
                new_data=new_rec
            )
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
        old_record = Database.execute_query(
            "SELECT * FROM camera WHERE id = %s",
            (camera_id,),
            fetch=True
        )

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
                set enabled = 0
                WHERE id = %s 
            """
            values=(camera_id,)
            result = Database.execute_query(query, values,fetch=False)
            if result:
                log_audit(
                    table_name="camera_audit",
                    action_type="DELETE",
                    old_data=old_record[0] if old_record else None,
                    new_data=None
                )
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

        old_record = Database.execute_query(
            "SELECT * FROM camera WHERE id = %s AND enabled = 1",
            (camera_id,),
            fetch=True
        )
        if not  old_record:
            return jsonify({"Message":" camera not found"}), 404

        query = f"""
            UPDATE camera
            SET {', '.join(fields_to_update)}
            WHERE id = %s
        """

        result = Database.execute_query(query, tuple(values_to_update), fetch=False)
        if result:
            new_record = Database.execute_query(
                "SELECT * FROM camera WHERE id = %s",
                (camera_id,),
                fetch=True
            )
            log_audit(
                table_name = "camera_audit",
                action_type="UPDATE",
                old_data = old_record[0],
                new_data=new_record[0] if new_record else None
            )
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
            INSERT INTO tablet (slc_id, room_id, name, mac_id, password, enabled, created_at,slc_edit)
            VALUES (%s, %s, %s, %s, %s, 1, NOW(),1)
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
        }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


# ENDPOINT 2: Delete tablet
@devices_bp.route('/delete_tablet/<int:tablet_id>',methods=['POST'])
def delete_tablet(tablet_id):
    try:
        query_test = """
            SELECT count(*) AS nbr
            FROM tablet 
            WHERE id=%s AND enabled = 1
        """
        values=(tablet_id,)
        result = Database.execute_query(query_test,values,fetch=True)
        if result[0]['nbr']==0:
            return jsonify({
                "Message":f"There is no Tablet with id: {tablet_id}"
            }),404
        else:
            query = """
                UPDATE tablet set enabled = 0 AND slc_edit = 1 WHERE id = %s AND enabled = 1
            """
            values=(tablet_id,)
            result = Database.execute_query(query,values,fetch=False)
            if result:
                return jsonify({
                    "Message":"Tablet deleted with Success"
                }),200
            else:
                return jsonify({
                    "Message":"Error in deleting tablet"
                })
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500


# ENDPOINT 3: Update table
@devices_bp.route('/update_tablet/<int:tablet_id>', methods=['POST'])
def update_tablet(tablet_id):
    try:
        data = request.get_json()

        allowed_fields = ['name', 'mac_id', 'password']

        # Filter only the fields that were actually sent
        fields_to_update = {key: data[key] for key in allowed_fields if key in data and data[key] != ''}

        # Nothing to update
        if not fields_to_update:
            return jsonify({
                "Message": "No valid fields provided to update"
            }), 400

        # Build query dynamically
        set_clause = ", ".join([f"{key} = %s" for key in fields_to_update])
        values = list(fields_to_update.values())
        values.append(tablet_id)

        query = f"UPDATE tablet SET {set_clause} WHERE id = %s"

        Database.execute_query(query, tuple(values), fetch=False)

        return jsonify({
            "Message": "Tablet updated successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


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
            WHERE enabled = 1
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


# ENDPOINT 3: Get tablet by ID
@devices_bp.route('/view-tablet/<int:id_tablette>', methods=['GET'])
# @token_required
def view_tablet_by_id(id_tablette):
    try:

        query = """
            SELECT t.id, t.name, t.mac_id, t.password, r.id, r.name, t.created_at, s.username
            FROM tablet t, room r,slc s
            WHERE t.id = %s AND t.enabled = 1 AND t.room_id = r.id AND r.enabled = 1 AND s.id = t.slc_id
        
        """
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
                "slc_mac": row["username"],
                "created_at": row["created_at"]

            })

        return jsonify(formatted_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500




@devices_bp.route('/create_door', methods=['POST'])
def create_door():
    try:
        data = request.get_json()
        required_fields = ['slc_id', 'room_id', 'mac_id', 'password', 'name']
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        if missing_fields:
            return jsonify({
                "Message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        query = """
            INSERT INTO slc_door (slc_id, room_id, mac_id, password, name)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (data.get('slc_id'), data.get('room_id'), data.get('mac_id'), data.get('password'), data.get('name'))
        Database.execute_query(query, values, fetch=False)

        new_record = Database.execute_query(
            "SELECT * FROM slc_door WHERE slc_id = %s AND mac_id = %s AND enabled = 1 ORDER BY id DESC LIMIT 1",
            (data.get('slc_id'), data.get('mac_id')),
            fetch=True
        )
        log_audit(
            table_name="slc_door_audit",
            action_type="INSERT",
            old_data=None,
            new_data=new_record[0] if new_record else None,
        )

        return jsonify({
            "Message": "slc_door created successfully"
        }), 200

    except Exception as e:
        print(e)
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@devices_bp.route('/delete_door/<int:door_id>', methods=['POST'])
def delete_door(door_id):
    try:
        query_test = """
            SELECT count(*) AS nbr
            FROM slc_door
            WHERE id = %s AND enabled = 1
        """
        result = Database.execute_query(query_test, (door_id,), fetch=True)
        if result[0]['nbr'] == 0:
            return jsonify({
                "Message": f"There is no Door with id: {door_id}"
            }), 404

        old_record = Database.execute_query(
            "SELECT * FROM slc_door WHERE id = %s AND enabled = 1",
            (door_id,),
            fetch=True
        )

        query = """
            UPDATE slc_door SET enabled = 0 WHERE id = %s AND enabled = 1
        """
        result = Database.execute_query(query, (door_id,), fetch=False)
        if result:
            log_audit(
                table_name="slc_door_audit",
                action_type="DELETE",
                old_data=old_record[0] if old_record else None,
                new_data=None,
            )
            return jsonify({
                "Message": "Door deleted with Success"
            }), 200
        else:
            return jsonify({
                "Message": "Error in deleting Door"
            }), 500

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@devices_bp.route('/update_door/<int:door_id>', methods=['POST'])
def update_door(door_id):
    try:
        data = request.get_json()

        query = """
            SELECT count(*) as nbr
            FROM slc_door
            WHERE id = %s
        """
        result = Database.execute_query(query, (door_id,), fetch=True)

        if result[0]['nbr'] == 0:
            return jsonify({
                "Message": "There is no door with this id"
            }), 404

        allowed_fields = {
            "name": "name",
            "status": "status",
            "mac_id": "mac_id",
            "password": "password",
            "room_id": "room_id"
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

        old_record = Database.execute_query(
            "SELECT * FROM slc_door WHERE id = %s AND enabled = 1",
            (door_id,),
            fetch=True
        )
        if not old_record:
            return jsonify({"Message": "slc_door not found"}), 404

        values_to_update.append(door_id)

        query = f"""
            UPDATE slc_door
            SET {', '.join(fields_to_update)}
            WHERE id = %s 
        """

        result = Database.execute_query(query, tuple(values_to_update), fetch=False)
        if result:
            new_record = Database.execute_query(
                "SELECT * FROM slc_door WHERE id = %s",
                (door_id,),
                fetch=True
            )
            log_audit(
                table_name="slc_door_audit",
                action_type="UPDATE",
                old_data=old_record[0],
                new_data=new_record[0] if new_record else None
            )
        return jsonify({
            "Message": "door updated successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@devices_bp.route('/get_all_door', methods=['GET'])
def get_all_door():
    try:
        query = """
            SELECT
                id,
                slc_id,
                name,
                mac_id AS mac,
                status,
                room_id AS roomId
            FROM slc_door
            WHERE enabled = 1
        """
        rows = Database.execute_query(query)

        formatted_data = []
        for row in rows:
            formatted_data.append({
                "id": row["id"],
                "name": row["name"],
                "mac": row["mac"],
                "status": row["status"],
                "roomId": row["roomId"],
            })

        return jsonify(formatted_data), 200

    except Exception as e:
        return jsonify({
            "Message": f"Erreur: {e} coming from server"
        }), 500


@devices_bp.route('/view_detail_door/<int:door_id>', methods=['GET'])
def view_detail_door(door_id):
    try:
        query = """
            SELECT d.id, d.slc_id, d.password, d.mac_id, r.name, d.created_at
            FROM slc_door d, room r          -- was: tablet t (wrong table + missing alias)
            WHERE d.room_id = r.id
              AND d.enabled = 1
              AND r.enabled = 1
              AND d.id = %s
        """
        rows = Database.execute_query(query, (door_id,))

        if not rows:
            return jsonify({
                "status": "error",
                "message": "door not found"
            }), 404

        formatted_data = []
        for row in rows:
            formatted_data.append({
                "id": row["id"],
                "name": row["name"],
                "mac": row["mac_id"],
                "password": row["password"],
                "slc_id": row["slc_id"],      # was: row["username"] (undefined)
                "created_at": row["created_at"]
            })

        return jsonify(formatted_data), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500



# ================================== Change Status door ==================================
def check_door_exist(mac_id):
    try:
        query = """
            SELECT * 
            FROM slc_door
            WHERE mac_id = %s AND enabled = 1
        """
        result = Database.execute_query(query,(mac_id,))
        return len(result)>0
    except Exception as e:
        return False

@devices_bp.route('/change_staus_door/<string:mac_id>', methods=['POST'])
def change_etat_door(mac_id):
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"Message": "Missing or invalid JSON body"}), 400

        status = data.get('status')

        if not(check_door_exist(mac_id)):
            return jsonify({
                "Message":"There is no Door with this mac_id"
            }),404

        query = """
            UPDATE slc_door
            SET oc = %s
            WHERE mac_id = %s AND enabled = 1
        """

        result = Database.execute_query(query, (status, mac_id), fetch=False)


        return jsonify({
            "Message": "Status updated with success"
        }),200

    except Exception as e:
        print(e)
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500