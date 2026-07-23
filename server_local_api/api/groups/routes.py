from flask import Blueprint,jsonify, request
import os
import sys
import json
from datetime import datetime
from config import Config
from core.database import Database
from core.middleware import token_required
from core.checks import *
from util.audit import log_audit


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ========================================
# Virtual User Endpoints
# ========================================

Group_bp = Blueprint('groups', __name__, url_prefix='/scl')

# ========================================
# ENDPOINT 1: Get groups with students by account and session
# ========================================
@Group_bp.route('/get-group/<int:account_id>/<int:session_id>', methods=['GET'])
def get_group(account_id, session_id):
    try:
       # Get groups with students in one query
       query = """
          SELECT 
             g.id,
             g.session_id,
             g.local_id,
             g.name,
             g.capacity,
             g.status,
             u.id as user_id,
             u.username,
             u.full_name,
             u.email,
             u.phone,
             r.id as relation_id

          FROM relation_group_local_session g
          LEFT JOIN relation_user_session r 
             ON r.relation_group_local_session_id = g.id 
             AND r.enabled = 1
          LEFT JOIN user u 
             ON u.id = r.user_id 
             AND u.enabled = 1
          WHERE g.session_id = %s 
             AND g.account_id = %s 
             AND g.enabled = 1 
             AND g.special_group IS NULL
          ORDER BY g.id, u.username
          LIMIT 1000
                """
       results = Database.execute_query(query, (session_id, account_id))

       relations_query = """
                 SELECT
				   rtsg.id as id,
				   rtsg.relation_group_local_session_id as group_id,
				   rtsg.subject_id,
				   rtsg.user_id as teacher_id,
				   COALESCE(sa.other_subject, sc.name) as subject_name,
				   t.username as teacher_name
				
				FROM relation_teacher_to_subject_group rtsg
				INNER JOIN relation_group_local_session g
				   ON g.id = rtsg.relation_group_local_session_id
				   AND g.session_id = %s
				   AND g.account_id = %s
				   AND g.enabled = 1
				   AND g.special_group IS NULL
				LEFT JOIN account_subject sa
				   ON sa.id = rtsg.subject_id
				   AND rtsg.subject_id = 1
				   AND sa.enabled = 1
				   AND sa.status = 1
				LEFT JOIN subject_config sc
				   ON sc.id = rtsg.subject_id
				   AND rtsg.subject_id != 1
				   AND sc.enabled = 1
				LEFT JOIN user t
				   ON t.id = rtsg.user_id
				   AND t.enabled = 1
				WHERE rtsg.enabled = 1 
				ORDER BY rtsg.relation_group_local_session_id, rtsg.id
              """
       relations_results = Database.execute_query(relations_query, (session_id, account_id))

       # Group the results by group_id
       groups = {}

       for row in results:
          group_id = row['id']

          # Create group entry if it doesn't exist
          if group_id not in groups:
             groups[group_id] = {
                'id': row['id'],
                'session_id': row['session_id'],
                'local_id': row['local_id'],
                'name': row['name'],
                'capacity': row['capacity'],
                'status': row['status'],
                'list_student': [],
                'relations': []
             }

          # Add student if exists (LEFT JOIN may return NULL)
          if row['user_id']:
             groups[group_id]['list_student'].append({
                'user_id': row['user_id'],
                'username': row['username'],
                'full_name': row['full_name'],
                'email': row['email'],
                'phone': row['phone'],
                'relation_id': row['relation_id']
             })

       # Attach teacher/subject relations to their group
       for row in relations_results:
          group_id = row['group_id']

          if group_id not in groups:
             continue

          groups[group_id]['relations'].append({
             'id': row['id'],
             'subject_id': row['subject_id'],
             'subject_name': row['subject_name'],
             'teacher_id': row['teacher_id'],
             'teacher_name': row['teacher_name']
          })

       # Convert dictionary to list
       groups_list = list(groups.values())
       return jsonify({
          "success": True,
          "data": groups_list,
          "count": len(groups_list)
       }), 200

    except Exception as err:
       print(f"Error: {err}")
       return jsonify({
          "success": False,
          "message": str(err),
          "data": [],
          "count": 0
       }), 500


# ========================================
# ENDPOINT 2: Affect user to group
# ========================================
@Group_bp.route('/affect_user_group/<int:session_id>', methods=['POST'])
def affect_user_group_endpoint(session_id):
	try:
		data = request.get_json()

		user_id = data.get('user_id')
		group_id = data.get('group_id')
		print(group_id)
		if not user_id or not group_id:
			return jsonify({
             "status": "error",
             "message": "Missing user_id or group_id"
          }), 400

		# Check if user exists
		query = """
            SELECT COUNT(id) as nbr FROM user WHERE id = %s AND enabled = 1
        """
		result = Database.execute_query(query, (user_id,))

		if not result or result[0]['nbr'] == 0:
			return jsonify({
             "status": "error",
             "message": "User not found"
          }), 404

		# Check if group exists
		query = """
            SELECT COUNT(id) as nbr FROM relation_group_local_session
            WHERE id = %s AND enabled = 1
        """
		result = Database.execute_query(query, (group_id,))

		if not result or result[0]['nbr'] == 0:
			return jsonify({
             "status": "error",
             "message": "Group not found"
          }), 404

		# Find the exact relation row that will be updated
		query = """
            SELECT id, user_id, session_id, relation_group_local_session_id
            FROM relation_user_session
            WHERE user_id = %s
                AND session_id = %s
                AND relation_group_local_session_id IS NULL
                AND enabled = 1
            ORDER BY id ASC
            LIMIT 1
        """
		relation_row = Database.execute_query(query, (user_id, session_id))

		if not relation_row:
			return jsonify({
             "status": "error",
             "message": "No available session slot found for this user"
          }), 404

		relation_row = relation_row[0]
		relation_id = relation_row['id']

		old_data = {
          "relation_user_session_id": relation_id,
          "user_id": user_id,
          "group_id": group_id,  # None before affect
          "session_id": session_id
       }

		# Update user's group assignment
		query = """
            UPDATE relation_user_session
            SET relation_group_local_session_id = %s
            WHERE id = %s
        """
		Database.execute_query(query, (group_id, relation_id), fetch=False)

		new_data = {
          "relation_user_session_id": relation_id,
          "user_id": user_id,
          "group_id": group_id,
          "session_id": session_id
       }

		log_audit(
          table_name="relation_group_local_session_audit",
          action_type="AFFECT",
          old_data=old_data,
          new_data=new_data
		)

		return jsonify({
          "status": "success",
          "message": f"User assigned to group successfully",
          "data": {
             "user_id": user_id,
             "group_id": group_id,
             "session_id": session_id
          }
       }), 200

	except Exception as e:
		print(f"Error: {e}")
		return jsonify({
          "status": "error",
          "message": f"Error: {str(e)}"
       }), 500

# ========================================
# ENDPOINT3 : Disaffect user group
# ========================================
@Group_bp.route('/disaffect_user_group/<int:session_id>', methods=['POST'])
def disaffect_user_group(session_id):
	try:
		if not session_exists(session_id):
			return jsonify({"Message": "There is not session with this id"}), 404

		data = request.get_json(silent=True)
		if not data:
			return jsonify({"Message": "Invalid or missing JSON body"}), 400

		group_id = data.get('group_id')
		user_id = data.get('user_id')
		if not group_id or not user_id:
			return jsonify({"Message": "group_id or user_id are required"}), 400

		user_query = "SELECT * FROM user WHERE id = %s"
		user = Database.execute_query(user_query, (user_id,), fetch=True)

		group_query = """
            SELECT * FROM relation_group_local_session
            WHERE id = %s AND session_id = %s
        """
		group = Database.execute_query(group_query, (group_id, session_id), fetch=True)

		if not user or not group:
			return jsonify({"Message": "User or Group not found"}), 404

		relation_query = """
            SELECT * FROM relation_user_session
            WHERE user_id = %s AND
                  session_id = %s AND
                  relation_group_local_session_id = %s AND
                  enabled = 1
        """
		relation = Database.execute_query(
            relation_query, (user_id, session_id, group_id), fetch=True
        )

		if not relation:
			return jsonify({"Message": "User is not part of this group"}), 404

		relation_row = relation[0]
		relation_id = relation_row['id']

		old_data = {
            "relation_user_session_id": relation_id,
            "user_id": user_id,
            "group_id": group_id,
            "session_id": session_id,
            "operation": "disaffect_user_from_group"
        }

		update_query = """
            UPDATE relation_user_session
            SET relation_group_local_session_id = NULL
            WHERE user_id = %s AND
                  session_id = %s AND
                  relation_group_local_session_id = %s AND
                  enabled = 1
		"""
		Database.execute_query(
			update_query, (user_id, session_id, group_id), fetch=False
		)

		new_data = {
            "relation_user_session_id": relation_id,
            "user_id": user_id,
            "group_id": group_id,
            "session_id": session_id,
            "operation": "disaffect_user_from_group"
        }

		log_audit(
            table_name="relation_group_local_session_audit",
            action_type="DISAFFECT",
            old_data=old_data,
            new_data=new_data
        )

		return jsonify({"Message": "User removed from group successfully."}), 200

	except Exception as e:
		print(e)
		return jsonify({
            "status": False,
            "Message": f"Error deleting group user: {e}"
        }), 500

# =============================================
# ENDPOINT 3: Get users not affected to groups
# =============================================
@Group_bp.route('/user_not_affected/<int:session_id>/<int:account_id>', methods=['GET'])
def get_user_not_affected(session_id, account_id):
	try:
		# Validate session exists and belongs to this account
		query = """
            SELECT id, name 
            FROM session 
            WHERE id = %s AND account_id = %s AND enabled = 1
        """
		session_data = Database.execute_query(query, (session_id, account_id))

		if not session_data:
			return jsonify({
				"status": "error",
				"message": "Session not found."
			}), 404

		# Get users NOT assigned to groups with relation IDs
		query = """
            SELECT 
                r.id as relation_id,
                r.user_id,
                u.full_name,
                u.username
            FROM relation_user_session r
            INNER JOIN user u ON u.id = r.user_id
            WHERE r.enabled = 1 
                AND u.enabled = 1 
                AND r.session_id = %s
                AND (r.relation_group_local_session_id IS NULL 
                     OR r.relation_group_local_session_id = 0)
            ORDER BY u.full_name
        """
		relations = Database.execute_query(query, (session_id,))

		# Group by user and build response
		users = {}

		for relation in relations:
			user_id = relation['user_id']

			if user_id not in users:
				users[user_id] = {
					'userId': user_id,
					'userName': relation['full_name'] or relation['username'],
					'sessionId': session_id,
					'sessionName': session_data[0]['name'],
					'sessionCount': 1,
				}
			else:
				users[user_id]['sessionCount'] += 1

		# Convert to list
		students = list(users.values())


		return jsonify({"students": students}), 200

	except Exception as e:
		print(f"Error: {e}")
		return jsonify({
			"status": "error",
			"message": "Unexpected error occurred."
		}), 500


# =============================================
# ENDPOINT 4: Delete group
# =============================================
@Group_bp.route('/delete-group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
	try:
		# Fetch old data before disabling, for the audit log
		old_query = "SELECT * FROM relation_group_local_session WHERE id = %s"
		old_result = Database.execute_query(old_query, (group_id,), fetch=True)

		if not old_result:
			return jsonify({"Message": "Group not found"}), 404

		old_data = old_result[0] if isinstance(old_result, list) else old_result

		print(group_id)
		# Disable the group
		query = """ 
            UPDATE relation_group_local_session
            SET enabled = 0
            WHERE id = %s     
        """
		values = (group_id,)
		result = Database.execute_query(query, values,fetch=False)
		# Check if any rows were affected
		if result == 0 or (isinstance(result, dict) and result.get('rowcount', 0) == 0):
			return jsonify({"Message": "Group not found"}), 404

		# Remove group association from users
		query2 = """
            UPDATE relation_user_session 
            SET relation_group_local_session_id = NULL 
            WHERE relation_group_local_session_id = %s
        """
		Database.execute_query(query2, values, fetch=False)

		# Log the disable action to the audit table
		new_data = dict(old_data)
		new_data['enabled'] = 0
		log_audit("relation_group_local_session_audit", "DELETE", old_data=old_data, new_data=new_data)

		return jsonify({"Message": "Group deleted successfully"}), 200

	except Exception as e:
		print(f"Error: {e} coming from delete group")
		return jsonify({"Message": f"Error: {str(e)}"}), 500

# =============================================
# ENDPOINT 5: Create group
# =============================================
@Group_bp.route('/create_group/<int:session_id>', methods=['POST'])
def create_group(session_id):
	try:
		data = request.get_json()
		relations = data.get('relations')

		if (not data.get('group_name') or not data.get('capacity')
				or not relations or not isinstance(relations, list)
				or not data.get('account_id') or not data.get('local_id')):
			return jsonify({"Message": "Missing required fields"}), 400

		for r in relations:
			if not r.get('subject_id') or not r.get('teacher_id'):
				return jsonify({"Message": "Each relation needs subject_id and teacher_id"}), 400

		local_id = data['local_id']
		account_id = data['account_id']
		name = data['group_name']
		capacity = data['capacity']
		status = 1
		enabled = 1
		special_group = data.get('special_group', None)
		access_type = data.get('access_type', 0)

		current_time = datetime.now()

		query = """
            INSERT INTO relation_group_local_session 
            (session_id, local_id, account_id, name, capacity, status, enabled, created_at, timestamp, special_group, access_type, slc_use)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, 1)
        """
		values = (session_id, local_id, account_id, name, capacity, status, enabled, special_group, access_type)

		result = Database.execute_query(query, values, fetch=False)

		if isinstance(result, int):
			group_id = result
		elif isinstance(result, dict) and 'lastrowid' in result:
			group_id = result['lastrowid']
		elif isinstance(result, dict) and 'id' in result:
			group_id = result['id']
		else:
			group_id = None

		query2 = """
		            INSERT INTO relation_teacher_to_subject_group
		            (relation_group_local_session_id, subject_id, user_id, enabled, created_at, timestamp, slc_use)
		            VALUES (%s, %s, %s, 1, NOW(), NOW(), 1)
		        """
		for r in relations:
			Database.execute_query(query2, (group_id, r['subject_id'], r['teacher_id']), fetch=False)

		# Log the new group to the audit table
		new_data = {
			"id": group_id,
			"session_id": session_id,
			"local_id": local_id,
			"account_id": account_id,
			"name": name,
			"capacity": capacity,
			"status": status,
			"enabled": enabled,
			"special_group": special_group,
			"access_type": access_type,
			"relations": relations
		}
		log_audit("relation_group_local_session_audit", "INSERT", new_data=new_data)

		return jsonify({
			"Message": "Group created successfully",
			"group_id": group_id
		}), 201

	except Exception as e:
		print(f"Error: {e} coming from create-group")
		return jsonify({"Message": f"Error: {str(e)}"}), 500


# =============================================
# ENDPOINT 6: Update_group
# =============================================
# =============================================
# ENDPOINT 6: Update_group
# =============================================
# =============================================
# ENDPOINT 6: Update_group
# =============================================
# =============================================
# ENDPOINT 6: Update_group
# =============================================
@Group_bp.route('/update_group/<int:group_id>', methods=['POST'])
def update_group(group_id):
	try:
		data = request.get_json()
		if not data:
			return jsonify({"Message": "No data provided"}), 400

		# Fetch old data before updating, for the audit log
		old_query = "SELECT * FROM relation_group_local_session WHERE id = %s AND enabled = 1"
		old_result = Database.execute_query(old_query, (group_id,), fetch=True)

		if not old_result:
			return jsonify({"Message": "Group not found"}), 404

		old_data = old_result[0] if isinstance(old_result, list) else old_result
		group_name = data.get('group_name')
		capacity = data.get('capacity')
		relations = data.get('relations', [])

		if not group_name or not capacity:
			return jsonify({"Message": "group_name and capacity are required"}), 400

		# Update the group
		query = """
            UPDATE relation_group_local_session
            SET name = %s, capacity = %s, timestamp = NOW()
            WHERE id = %s AND enabled = 1
        """
		values = (group_name, capacity, group_id)
		result = Database.execute_query(query, values, fetch=False)

		if result == 0 or (isinstance(result, dict) and result.get('rowcount', 0) == 0):
			return jsonify({"Message": "Group not found"}), 404

		# Snapshot old relations for the audit log / diffing
		old_relations_query = """
            SELECT id, subject_id, user_id AS teacher_id
            FROM relation_teacher_to_subject_group
            WHERE relation_group_local_session_id = %s AND enabled = 1
        """
		old_relations_result = Database.execute_query(old_relations_query, (group_id,), fetch=True)
		old_relations = old_relations_result if old_relations_result else []
		old_relations_by_id = {int(r['id']): r for r in old_relations}

		# ---------------------------------------------------------------
        # Diff old relations vs incoming relations (by relation_id) so the
        # audit log records exactly what was added / updated / deleted.
        # ---------------------------------------------------------------
		added_relations = []       # [{teacher_id, subject_id}, ...]
		updated_relations = []     # [{id, teacher_id, subject_id}, ...]  (new values)
		seen_old_ids = set()

		for relation in relations:
			subject_id = relation.get('subject_id')
			teacher_id = relation.get('teacher_id')
			relation_id = relation.get('relation_id')

			if not subject_id or not teacher_id:
				continue

			if relation_id and int(relation_id) in old_relations_by_id:
				relation_id = int(relation_id)
				seen_old_ids.add(relation_id)
				old_rel = old_relations_by_id[relation_id]

				if int(old_rel['subject_id']) != int(subject_id) or int(old_rel['teacher_id']) != int(teacher_id):
					updated_relations.append({
                        "id": relation_id,
                        "teacher_id": teacher_id,
                        "subject_id": subject_id
                    })
			else:
				added_relations.append({
                    "teacher_id": teacher_id,
                    "subject_id": subject_id
                })

		deleted_relation_ids = [
            old_id for old_id in old_relations_by_id.keys()
            if old_id not in seen_old_ids
        ]

		# Replace teacher/subject relations: disable old ones, insert new ones
		disable_relations_query = """
            UPDATE relation_teacher_to_subject_group
            SET enabled = 0
            WHERE relation_group_local_session_id = %s AND enabled = 1
        """
		Database.execute_query(disable_relations_query, (group_id,), fetch=False)

		for relation in relations:
			subject_id = relation.get('subject_id')
			teacher_id = relation.get('teacher_id')

			if not subject_id or not teacher_id:
				continue

			insert_relation_query = """
                INSERT INTO relation_teacher_to_subject_group
                (relation_group_local_session_id, subject_id, user_id, enabled, created_at, timestamp, slc_use)
                VALUES (%s, %s, %s, 1, NOW(), NOW(), 1)
            """
			Database.execute_query(
                insert_relation_query,
                (group_id, subject_id, teacher_id),
                fetch=False
            )

		# -----------------------------------------------------------
        # Build new_data in the "dynamic index in key name" shape
        # (always present, even when empty)
        # -----------------------------------------------------------
		delete_idx = ",".join(str(i) for i in range(len(deleted_relation_ids)))
		update_idx = ",".join(str(i) for i in range(len(updated_relations)))
		new_idx = ",".join(str(i) for i in range(len(added_relations)))

		new_data = {
			"id": group_id,
			"name": group_name,
			"capacity": capacity,
			f"deleteRelationIds[{delete_idx}]": deleted_relation_ids,
			f"updateRelations[{update_idx}]": [
				{"id": r["id"], "teacherId": r["teacher_id"], "subjectId": r["subject_id"]}
				for r in updated_relations
			],
			f"newRelationTeacherId[{new_idx}]": [r["teacher_id"] for r in added_relations],
			f"newRelationSubjectId[{new_idx}]": [r["subject_id"] for r in added_relations]
		}

		old_data = dict(old_data)
		old_data['relations'] = old_relations

		log_audit(
            "relation_group_local_session_audit",
            "UPDATE",
            old_data=old_data,
            new_data=new_data
		)
		return jsonify({"Message": "Group updated successfully"}), 200

	except Exception as e:
		print(f"Error: {e} coming from update-group")
		return jsonify({"Message": f"Error: {str(e)}"}), 500