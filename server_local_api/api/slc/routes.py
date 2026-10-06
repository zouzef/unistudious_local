from flask import Blueprint, jsonify, send_file, request
import sys
import os
from datetime import datetime
import json
import traceback

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
def get_all_rooms():
	try:
		query = "SELECT * FROM room WHERE enabled = 1"
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

		query = """
            SELECT 
                l.*,
                sl.slc_id as slc_id,
                COALESCE(SUM(CAST(r.capacity AS UNSIGNED)), 0) as capacity
            FROM local l
            JOIN slc_local sl ON sl.local_id = l.id
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



def log_room_audit(action_type, old_data=None, new_data=None):
	"""Insert a row in room_audit. Never breaks the main request."""
	print(f"[AUDIT] called: {action_type}")
	try:
		query = """
            INSERT INTO room_audit (action_type, old_data, new_data)
            VALUES (%s, %s, %s)
        """
		res = Database.execute_query(
            query,
            (
                action_type,
                json.dumps(old_data, default=str) if old_data is not None else None,
                json.dumps(new_data, default=str) if new_data is not None else None,
            ),
            fetch=False,
        )
		print(f"[AUDIT] insert result: {res}")
	except Exception:
		print("[AUDIT] FAILED:")
		traceback.print_exc()


@slc_bp.route('/create_room', methods=['POST'])
def create_room():
	try:
		data = request.get_json(silent=True) or request.form.to_dict()
		print("[CREATE] data:", data)
		if not data:
			return jsonify({"Message": "There is no data"}), 400

		name = (data.get('name') or '').strip()
		capacity = data.get('capacity')
		local_id = data.get('local_id')
		if not name or not capacity or not local_id:
			return jsonify({"Message": "Missing required parameter"}), 400

		try:
			capacity = int(capacity)
			local_id = int(local_id)
		except (TypeError, ValueError):
			return jsonify({"Message": "Capacity and local_id must be numbers"}), 400

		results = Database.execute_query(
			"SELECT COUNT(*) AS nbr FROM room WHERE name = %s AND local_id = %s AND enabled = 1",
			(name, local_id), fetch=True
		)
		print("[CREATE] name check:", results)
		if results and results[0]['nbr'] > 0:
			return jsonify({"Message": "There is already a room with this name in this local"}), 400

		result = Database.execute_query(
			"INSERT INTO room (name, capacity, local_id, enabled) VALUES (%s, %s, %s, %s)",
			(name, capacity, local_id, True), fetch=False
		)
		print("[CREATE] insert result:", result)

		if result:
			log_room_audit(
				"INSERT",
				old_data=None,
				new_data={"id": result, "name": name, "capacity": capacity, "local_id": local_id, "enabled": 1},
			)
			return jsonify({
				"Success": True,
				"Message": "Room created successfully",
				"data": {"id": result}
			}), 200
		return jsonify({"Message": "Failed to create the room"}), 400

	except Exception as e:
		traceback.print_exc()
		return jsonify({"Message": f"Error: {e} coming from backend"}), 500


@slc_bp.route('/delete_room/<int:room_id>', methods=['POST'])
def delete_room(room_id):
	try:
		query_old = """
			SELECT id, id_prod, name, capacity, local_id, enabled
			FROM room
			WHERE id = %s AND enabled = 1
		"""
		old_rows = Database.execute_query(query_old, (room_id,), fetch=True)
		if not old_rows:
			return jsonify({"Message": "Room not found"}), 404
		old_room = old_rows[0]

		query = """
			UPDATE room
			SET enabled = 0
			WHERE id = %s
		"""
		# don't rely on the return value: for UPDATE it is lastrowid (0)
		Database.execute_query(query, (room_id,), fetch=False)

		log_room_audit(
			"DELETE",
			old_data=old_room,
			new_data={**old_room, "enabled": 0},
		)

		return jsonify({
			"Success": True,
			"Message": "Room deleted successfully"
		}), 200

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500


@slc_bp.route('/update_room/<int:room_id>', methods=['POST'])
def update_room(room_id):
	try:
		data = request.get_json(silent=True) or request.form.to_dict()
		if not data:
			return jsonify({"Message": "There is no data to update"}), 400

		name = (data.get('name') or '').strip()
		capacity = data.get('capacity')
		if not name or capacity in (None, ''):
			return jsonify({"Message": "Missing required parameter"}), 400

		try:
			capacity = int(capacity)
		except (TypeError, ValueError):
			return jsonify({"Message": "Capacity must be a number"}), 400

		# fetch the full old row (needed for the audit log), including local_id and id_prod
		query_old = """
			SELECT id, id_prod, name, capacity, local_id, enabled
			FROM room
			WHERE id = %s AND enabled = 1
		"""
		old_rows = Database.execute_query(query_old, (room_id,), fetch=True)
		if not old_rows:
			return jsonify({"Message": "Room not found"}), 404
		old_room = old_rows[0]

		update_query = """
			UPDATE room
			SET name = %s, capacity = %s
			WHERE id = %s AND enabled = 1
		"""
		# don't rely on the return value: for UPDATE it is lastrowid (0)
		Database.execute_query(update_query, (name, capacity, room_id), fetch=False)

		log_room_audit(
			"UPDATE",
			old_data=old_room,
			new_data={**old_room, "name": name, "capacity": capacity},
		)

		return jsonify({
			"Success": True,
			"Message": "Room updated successfully"
		}), 200

	except Exception as e:
		return jsonify({
			"Message": f"Error: {e} coming from backend"
		}), 500

# ENDPOINT 3: Get slc id
@slc_bp.route('/get_slc_id', methods=['GET'])
def get_slc_id():
	try:
		query = """
            SELECT * FROM slc LIMIT 1;
        """
		result = Database.execute_query(query)
		if result:
			return jsonify({
				"Message": "Success",
				"data": result,
			}), 200
		else:
			return jsonify({
				"Message": "Bad requests",
				"data": None
			}), 404
	except Exception as e:
		return jsonify({"Message": f"Error: {e}"}), 500


# ENDPOINT 4: GET Academie Name
@slc_bp.route('/get_academie_info/<tablet_id>', methods=['GET'])
def get_academie_info(tablet_id):
	try:
		query = """
            SELECT a.name, t.id 
            FROM tablet t, account a, slc s 
            WHERE 
                t.mac_id = %s 
                AND t.slc_id = s.id
                AND s.account_id = a.id;
        """
		rows = Database.execute_query(query, (tablet_id,), fetch=True)
		if not rows:
			return jsonify({
				"status": "error",
				"message": "No academie found for this tablet"
			}), 404

		return jsonify({
			"status": "ok",
			"data": rows[0]
		}), 200

	except Exception as e:
		print(f"Error: {e} coming from get_academie_info")
		return jsonify({
			"status": "error",
			"message": "Error coming from get_academie_info"
		}), 500


# ENDPOINT 5: Get Academie Image
@slc_bp.route('/get_academie_image/<int:tablet_id>', methods=['GET'])
def get_academie_image(tablet_id):
	try:
		query = """
            SELECT a.file_link, a.id 
            FROM tablet t, account a, slc s 
            WHERE 
                t.mac_id = %s 
                AND t.slc_id = s.id
                AND s.account_id = a.id;
        """
		rows = Database.execute_query(query, (tablet_id,))

		if not rows:
			return jsonify({
				"status": "error",
				"message": "No academie found for this tablet"
			}), 404

		account_id = rows[0]["id"]
		file_link = rows[0]["file_link"]

		if not file_link:
			return jsonify({
				"status": "error",
				"message": "No image found for this academie"
			}), 404

		# Build path relative to this file → no absolute path
		base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		image_path = os.path.join(base_dir, "uploads", "academie_img", f"academie_{account_id}", file_link)
		if not os.path.exists(image_path):
			return jsonify({
				"status": "error",
				"message": "Image file not found on server"
			}), 404

		return send_file(image_path)

	except Exception as e:
		print(f"Error: {e} coming from get_academie_image")
		return jsonify({
			"status": "error",
			"message": "Error coming from get_academie_image"
		}), 500


# ENDPOINT 6: health
@slc_bp.route('/health', methods=['GET'])
def health():
	return jsonify({"status": "ok"}), 200
