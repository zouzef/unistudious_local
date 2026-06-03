from flask import Blueprint, jsonify, request
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from util.audit import log_audit

formation_bp = Blueprint('formation', __name__, url_prefix='/scl')

# Service check formation
def check_formation(formation_id):
	try:
		query = """
					SELECT COUNT(*) AS nbr
					FROM formation 
					WHERE id=%s AND enabled = 1
				"""
		values = (formation_id,)
		result = Database.execute_query(query, values, fetch=True)

		return result[0]['nbr'] > 0

	except Exception as e:
		return False


@formation_bp.route('/get-formation-info/<int:account_id>',methods=['GET'])
def get_formation_info(account_id):
	try:
		query = """
			SELECT 
					f.id,
				   f.name,
				   f.description,
				   f.type_session,
				   f.number_day_duration,
				   f.number_session,
				   f.condition_of_passage,
				   f.status
			 FROM formation f
			WHERE f.account_id = %s AND f.enabled = 1
		"""
		values = (account_id,)
		result = Database.execute_query(query,values)

		if result :
			return jsonify({
				"Data":result
			}),200
		else:
			return jsonify({
				"Message":"Error",
				"Data":[]
			}),404


	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from get_formation_info"
		}),500


@formation_bp.route('/delete_formation/<int:formation_id>/<int:account_id>', methods=['POST'])
def delete_formation(formation_id, account_id):
    try:
        if not check_formation(formation_id):
            return jsonify({
                "Message": "There is no formation with this id"
            }), 404

        # ✅ Get old record before delete
        old_record = Database.execute_query(
            """
            SELECT *
            FROM formation
            WHERE id = %s AND account_id = %s
            """,
            (formation_id, account_id),
            fetch=True
        )

        query = """
            UPDATE formation
            SET enabled = 0,
                updated_at = NOW()
            WHERE id = %s
              AND account_id = %s
        """

        result = Database.execute_query(
            query,
            (formation_id, account_id),
            fetch=False
        )

        if result:

            # ✅ Audit log
            log_audit(
				table_name="formation_audit",
                action_type="DELETE",
                old_data=old_record[0] if old_record else None,
                new_data=None
            )

            return jsonify({
                "Message": "Formation deleted with success"
            }), 200

        return jsonify({
            "Message": "Failed to delete formation"
        }), 400

    except Exception as e:
        print(e)
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


@formation_bp.route('/view_formation/<int:formation_id>',methods=['GET'])
def view_formation(formation_id):
	try:
		if not(check_formation(formation_id)):
			return jsonify({
				"Message":"There is no formation with this id"
			}),404
		query = """
		    SELECT 
				DISTINCT
				f.name,
				f.status,
				f.type_date,
				f.number_day_duration,
				f.number_session,
				f.type_session,
				f.condition_of_passage,
				f.public_resource,
				f.description
			FROM formation f
			
			WHERE f.id = %s AND f.enabled = 1
		"""
		result = Database.execute_query(query,(formation_id,),fetch=True)
		return jsonify(result),200

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		})

@formation_bp.route('/update_formation/<int:formation_id>', methods=['POST'])
def update_formation(formation_id):
    try:
        data = request.get_json()

        # ✅ Get old record before update
        old_record = Database.execute_query(
            """
            SELECT *
            FROM formation
            WHERE id = %s
              AND enabled = 1
            """,
            (formation_id,),
            fetch=True
        )

        if not old_record:
            return jsonify({
                "Message": "Formation not found"
            }), 404

        allowed_fields = [
            'name',
            'status',
            'type_date',
            'number_day_duration',
            'number_session',
            'type_session',
            'condition_of_passage',
            'public_resource',
            'description',
            'account_section_id',
            'account_level_id'
        ]

        fields_to_update = {
            k: v for k, v in data.items()
            if k in allowed_fields
        }

        if not fields_to_update:
            return jsonify({
                "Message": "No fields provided to update"
            }), 400

        set_clause = ", ".join(
            [f"{k} = %s" for k in fields_to_update.keys()]
        )

        values = list(fields_to_update.values())
        values.append(formation_id)

        query = f"""
            UPDATE formation
            SET {set_clause},
                updated_at = NOW()
            WHERE id = %s
        """

        result = Database.execute_query(
            query,
            values,
            fetch=False
        )

        if result:

            # ✅ Get new record after update
            new_record = Database.execute_query(
                """
                SELECT *
                FROM formation
                WHERE id = %s
                """,
                (formation_id,),
                fetch=True
            )

            # ✅ Audit log
            log_audit(
				table_name="formation_audit",
                action_type="UPDATE",
                old_data=old_record[0],
                new_data=new_record[0] if new_record else None
            )

            return jsonify({
                "Message": "Formation updated successfully"
            }), 200

        return jsonify({
            "Message": "Error updating formation"
        }), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

@formation_bp.route('/create_formation/<int:account_id>', methods=['POST'])
def create_formation(account_id):
    try:
        data = request.get_json()

        required_fields = [
            'name',
            'status',
            'typeDate',
            'typeSession',
            'conditionOfPassage'
        ]

        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "Message": f"'{field}' is required"
                }), 400

        name                                         = data.get('name', '').strip()
        status                                       = data.get('status')
        account_level_id                             = data.get('accountLevel') or None
        account_section_id                           = data.get('accountSection') or None
        type_date                                    = data.get('typeDate')
        other_type_date                              = data.get('otherTypeDate', '').strip() or None
        number_day_duration                          = data.get('numberDayDuration') or None
        number_session                               = data.get('numberSession') or None
        type_session                                 = data.get('typeSession')
        other_type_session                           = data.get('otherTypeSession', '').strip() or None
        condition_of_passage                         = data.get('conditionOfPassage')
        condition_of_passage_formule                 = data.get('conditionOfPassageFormule') or None
        condition_of_passage_formule_by_note         = data.get('conditionOfPassageFormuleByNote', '').strip() or None
        condition_of_passage_formule_by_present      = data.get('conditionOfPassageFormuleByPresent', '').strip() or None
        condition_of_passage_formule_by_note_present = data.get('conditionOfPassageFormuleByNotePresent', '').strip() or None
        public_resource                              = data.get('publicResource') or None
        description                                  = data.get('description', '').strip() or None
        img_link                                     = data.get('imgLink') or None

        query = """
            INSERT INTO formation (
                account_id,
                account_level_id,
                account_section_id,
                name,
                description,
                status,
                type_date,
                other_type_date,
                type_session,
                other_type_session,
                number_day_duration,
                number_session,
                condition_of_passage,
                condition_of_passage_formule,
                condition_of_passage_formule_by_note,
                condition_of_passage_formule_by_present,
                condition_of_passage_formule_by_note_present,
                img_link,
                public_resource,
                enabled,
                created_at,
                updated_at
            ) VALUES (
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,
                1,
                NOW(),NOW()
            )
        """

        values = [
            account_id,
            account_level_id,
            account_section_id,
            name,
            description,
            status,
            type_date,
            other_type_date,
            type_session,
            other_type_session,
            number_day_duration,
            number_session,
            condition_of_passage,
            condition_of_passage_formule,
            condition_of_passage_formule_by_note,
            condition_of_passage_formule_by_present,
            condition_of_passage_formule_by_note_present,
            img_link,
            public_resource
        ]

        result = Database.execute_query(
            query,
            values,
            fetch=False
        )

        if result:

            # ✅ Get inserted record
            new_record = Database.execute_query(
                """
                SELECT *
                FROM formation
                WHERE id = LAST_INSERT_ID()
                """,
                fetch=True
            )

            # ✅ Audit log
            log_audit(
				table_name="formation_audit",
                action_type="INSERT",
                old_data=None,
                new_data=new_record[0] if new_record else data
            )

            return jsonify({
                "Message": "Formation created successfully"
            }), 200

        return jsonify({
            "Message": "Error creating formation"
        }), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500

