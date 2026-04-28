from flask import Blueprint, jsonify, request,send_file
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required
import uuid
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


#ENDPOINT 2: Get session image
@sessions_bp.route('/get_session_image/<int:session_id>',methods=['GET'])
def get_session_image(session_id):
    try:
        query = """
            SELECT img_link FROM session WHERE id = %s
        """
        values = (session_id,)
        result = Database.execute_query(query,values,fetch=True)

        if not result :
            # Session not found - return defalt image
                default_img_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    'static/assets/images/session-defult.png'
                )
                return send_file(default_img_path)
        img_filename = result[0]['img_link']

        # If session has no image set, return default
        if not img_filename or img_filename.strip() == '':
            default_img_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'static/assets/images/session-defult.png'
            )
            return send_file(default_img_path)

        BASE_UPLOAD_FOLDER = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            f'uploads/session_img/session_{session_id}'
        )
        img_path = os.path.join(BASE_UPLOAD_FOLDER, img_filename)

        # If image file doesn't exist, return default
        if not os.path.exists(img_path):
            print(f"⚠️ Image not found at {img_path}, returning default")
            default_img_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'static/assets/images/session-defult.png'
            )
            return send_file(default_img_path)

        return send_file(img_path)


    except Exception as e:
        print(f"Error: {e} coming from get_session_image")
        #Return default image on error instead of 500
        try:
            default_img_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'static/assets/images/session-defult.png'
            )
            return send_file(default_img_path)
        except Exception as e:
            return jsonify({
                "Message":"Error loading image"
            }),500


#ENDPOINT 3: Create session
@sessions_bp.route('/create-session', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        new_uuid = str(uuid.uuid4())
        required_keys = [
            'account_id',
            'name',
            'formation',
            'capacity',
            'typePay',
            'paymentMethode',

            'userRegisterAfterStart',
            'startDate',
            'endDate',
            'requestChangeGroup',
        ]

        missing_keys = [key for key in required_keys if key not in data]
        null_keys = [key for key in required_keys if key in data and (data[key] is None or data[key] == '')]

        if missing_keys:
            return jsonify({"Message": f"Missing required keys: {missing_keys}"}), 400

        if null_keys:
            return jsonify({"Message": f"These keys cannot be null: {null_keys}"}), 400

        query = """
            INSERT INTO session 
            (
                account_id, name, formation_id, capacity,
                type_pay, number_session_for_pay, price_student_absent,
                payment_methode, price, price_presence, price_online,
                currency, user_register_after_start, start_date, end_date,
                request_change_group, max_group_change, special_group,
                public_resource, description, img_link,uuid
            )
            VALUES(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                'TND',
                %s, %s, %s, %s, %s, %s, %s, %s, %s,%s
            );
        """

        values = (
            data.get('account_id'),
            data.get('name'),
            data.get('formation'),
            data.get('capacity'),
            data.get('typePay'),
            data.get('numberSessionForPay') or None,
            data.get('priceStudentAbsent') or None,
            data.get('paymentMethode'),
            data.get('price') or None,
            data.get('pricePresence') or None,
            data.get('priceOnline') or None,
            data.get('userRegisterAfterStart'),
            data.get('startDate'),
            data.get('endDate'),
            data.get('requestChangeGroup'),
            data.get('maxGroupChange') or None,
            data.get('specialGroup') or None,
            data.get('publicResource') or None,
            data.get('description'),
            data.get('logoFile'),
            new_uuid
        )

        result = Database.execute_query(query, values,fetch=False)      # ← execute the query
        print("resultat:",result)

        return jsonify({"Message": "Session created with success"}), 200

    except Exception as e:
        print(f"Error: {e} coming from create session")
        return jsonify({"Message": f"Error {e} in creating session"}), 500


#ENDPOINT 4: Get session info
@sessions_bp.route('/get_session_info/<int:session_id>', methods=['GET'])
def get_session_info(session_id):
    try:
        query = """
            SELECT * 
            FROM session s
            WHERE s.id = %s AND s.enabled = 1
        """
        values = (session_id,)  # ✅ proper tuple
        result = Database.execute_query(query, values, fetch=True)
        if result:
            return jsonify(
                result
            ), 200
        else:
            return jsonify({
                "Message": "No data for this session"
            }), 400

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e}"
        }), 500


#ENDPOINT 5: Update session
@sessions_bp.route('/update_session/<int:session_id>', methods=['POST'])
def update_session(session_id):
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"Message": "No data received"}), 400

        print(f"📋 Updating session {session_id} with: {data}")

        query = """
            UPDATE session
            SET
                name                      = %s,
                formation_id              = %s,
                capacity                  = %s,
                type_pay                  = %s,
                number_session_for_pay    = %s,
                price_student_absent      = %s,
                payment_methode           = %s,
                price                     = %s,
                price_presence            = %s,
                price_online              = %s,
                currency                  = %s,
                user_register_after_start = %s,
                start_date                = %s,
                end_date                  = %s,
                request_change_group      = %s,
                max_group_change          = %s,
                special_group             = %s,
                public_resource           = %s,
                description               = %s,
                season_id                 = %s,
                updated_at                = NOW()
            WHERE id = %s AND enabled = 1
        """

        values = (
            data.get('name'),
            data.get('formation') or None,
            data.get('capacity'),
            data.get('typePay'),
            data.get('numberSessionForPay') or None,
            data.get('priceStudentAbsent') or None,
            data.get('paymentMethode') or None,
            data.get('price') or None,
            data.get('pricePresence') or None,
            data.get('priceOnline') or None,
            data.get('currency') or None,
            data.get('userRegisterAfterStart'),
            data.get('startDate'),
            data.get('endDate'),
            data.get('requestChangeGroup') or None,
            data.get('maxGroupChange') or None,
            data.get('specialGroup') or None,
            data.get('publicResource') or None,
            data.get('description'),
            data.get('season') or None,
            session_id
        )

        Database.execute_query(query, values, fetch=False)

        return jsonify({
            "Message": "Session updated with success",
            "session_id": session_id
        }), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500


#ENDPOINT 6: Delete session
@sessions_bp.route('/delete_session/<int:session_id>', methods=['POST'])
def delete_session(session_id):
    try:
        # First check if session exists and is enabled
        check_query = "SELECT id FROM session WHERE id = %s AND enabled = 1"
        exists = Database.execute_query(check_query, (session_id,), fetch=True)

        if not exists:
            return jsonify({
                "Message": "Session not found"
            }), 404

        # Soft delete
        query = """
            UPDATE session 
            SET enabled = 0 
            WHERE id = %s
        """
        Database.execute_query(query, (session_id,), fetch=False)

        return jsonify({
            "Message": "Session Deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "Message": f"Error: {e} in deleting session"
        }), 500


#ENDPOINT 7: GET all_user_session
@sessions_bp.route('/get_all_user_session/<int:session_id>',methods=['GET'])
def get_all_user_sesssion(session_id):
    try:
        query = """
            SELECT COUNT(DISTINCT user_id) as nbruser 
            FROM relation_user_session 
            WHERE session_id = %s AND enabled = 1;
        """
        values = (session_id,)
        result = Database.execute_query(query,values,fetch=True)
        return jsonify(result[0]['nbruser']), 200

    except Exception as e:
        print(f"Error: {e} in get_all_user_session")
        return jsonify({"Message": f"Error: {e} in get_all_user_session"}), 500


#ENDPOINT 8: GET all_group_session
@sessions_bp.route('/get_all_group_session/<int:session_id>', methods=['GET'])
def get_all_group_session(session_id):
    try:
        query = """
            SELECT COUNT(DISTINCT id) as nbrgrp
            FROM relation_group_local_session 
            WHERE enabled = 1 AND session_id = %s 
        """
        values = (session_id,)
        result = Database.execute_query(query, values, fetch=True)
        if result:
            return jsonify({"nbrgroup": result[0]['nbrgrp']}), 200
        else:
            return jsonify({"Message": "No group found for this session"}), 400
    except Exception as e:
        return jsonify({"Message": f"Error: {e} in getting all group_session"}), 500


#ENDPOINT 9: GET user_session_info
@sessions_bp.route('/get_user_session_info/<int:session_id>',methods=['GET'])
def get_user_session_info(session_id):
    try:
        query = """
            SELECT DISTINCT rus.*,u.username
            FROM relation_user_session rus,user u
            WHERE rus.enabled = 1 AND rus.session_id = %s AND rus.user_id = u.id
        
        """
        values = (session_id,)
        result = Database.execute_query(query,values,fetch=True)
        if result:
            return jsonify({
                "Data": result
            }),200
        else:
            return jsonify({
                "Message":"There is no data for this session"
            }),400

    except Exception as e:
        print(f"Error: {e} coming from get user_session_info")
        return jsonify({
            "Message":f"Error: {e} coming from get_user_session_info"
        }),500