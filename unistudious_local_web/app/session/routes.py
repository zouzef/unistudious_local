# app/session/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
import io
import os
import base64
from app.session.service import (
    get_all_sessions, get_moderator,
    get_locals, get_room, get_teacher,
    get_session_image,
    create_session_local,
    get_session_info_service,
    update_session_service,
    delete_session_service,
    get_all_group_session_service,
    get_all_user_service
)

session_bp = Blueprint('session', __name__)


# ==========================================
# PAGE ROUTES
# ==========================================

@session_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Main dashboard page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id', 3)

    return render_template('index.html',
                           sessions=get_all_sessions(account_id),
                           data_modera=get_moderator(account_id),
                           local_details=get_locals(account_id),
                           account_id=account_id,
                           page='home')


@session_bp.route('/dashboard/show-session')
def show_sessions():
    """Display all sessions page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id', 3)

    return render_template('index.html',
                           sessions=get_all_sessions(account_id),
                           account_id=account_id,
                           page='show-session')


@session_bp.route('/dashboard/create-session', methods=['GET'])
def create_session():
    """Create new session page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    account_id = session.get('account_id', 3)
    return render_template('index.html',
                           account_id=account_id,
                           page='create-session')


@session_bp.route('/dashboard/view-session/<int:session_id>', methods=['GET'])
def view_session(session_id):
    """Update session page"""
    print(f"\n \n \n \n \n \n \n \n {session_id} \n \n")
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    account_id = session.get('account_id', 3)
    return render_template('index.html',
                           account_id=account_id,
                           page='view_session')


@session_bp.route('/dashboard/show-session-config/<int:id_session>', methods=['GET'])
def show_session_config(id_session):
    """Session configuration page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id', 3)

    from app.session.service import get_locals, get_all_sessions, get_moderator
    from app.calendar.service import get_calendar_per_session

    return render_template('index.html',
                           id_session=id_session,
                           account_id=account_id,
                           local_details=get_locals(account_id),
                           sessions=get_all_sessions(account_id),
                           data_modera=get_moderator(account_id),
                           calendar_data=get_calendar_per_session(account_id, id_session),
                           page='session_config')


@session_bp.route('/dashboard/show-all-user-session/<int:id_session>', methods=['GET'])
def show_user_session(id_session):

    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('index.html',
                           id_session=id_session,
                           account_id=session.get('account_id'),
                           page='show_user_session')

# ==========================================
# API ROUTES
# ==========================================

@session_bp.route('/api/get-sessions/<int:account_id>', methods=['GET'])
def api_get_sessions(account_id):
    """Get all sessions as JSON"""
    result = get_all_sessions(account_id)
    return jsonify(result), 200


@session_bp.route('/api/get_room/<int:local_id>')
def api_get_room(local_id):
    """Get rooms from local"""
    result = get_room(local_id)
    return jsonify({"Message": "Success", "Room": result}), 200


@session_bp.route('/api/get_teacher/<int:session_id>')
def api_get_teacher(session_id):
    """Get teachers from session"""
    result = get_teacher(session_id)
    if result:
        return jsonify({"Message": "Success", "teacher": result}), 200
    return jsonify({"Message": "No teacher found", "teacher": []}), 404


@session_bp.route('/api/get_session_img/<int:session_id>', methods=['GET'])
def api_get_session_img(session_id):
    """Get session image"""
    content, mimetype = get_session_image(session_id)

    if content:
        return send_file(
            io.BytesIO(content),
            mimetype=mimetype,
            as_attachment=False
        )

    # Return default image
    try:
        default_img_path = os.path.join(
            current_app.root_path,
            '../static/assets/images/session-default.png'
        )
        return send_file(default_img_path, mimetype='image/png')
    except Exception:
        transparent_png = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        return send_file(io.BytesIO(transparent_png), mimetype='image/png')


@session_bp.route('/api/create-session', methods=['POST'])
def create_session_route():  # 👈 rename this
    try:
        session_data = request.get_json()
        print(session_data)
        status, code = create_session_local(session_data)  # this calls the service
        if status and code == 200:
            return jsonify({"Message": "Session created with success"}), 200
        else:
            return jsonify({"Message": "Error in creating session"}), 400
    except Exception as e:
        print(f"Error:{e}")
        return jsonify({"Message": "Error coming from create_session"}), 500


@session_bp.route('/api/get-local-info/<int:account_id>', methods=['GET'])
def get_local_info(account_id):
    try:
        local_data = get_locals(account_id)
        if local_data:
            return jsonify({"Data": local_data}), 200  # ← fixed
        else:
            return jsonify({"Message": "No local data"}), 400
    except Exception as e:
        return jsonify({"Message": f"Error coming from get_local_info: {e}"}), 500


@session_bp.route('/api/get-session-info/<int:session_id>', methods=['GET'])
def get_session_info(session_id):
    try:
        result,session_info = get_session_info_service(session_id)
        if result:
            return jsonify(session_info), 200
        print(session_info)
    except Exception as e:
        print(f"Error: {e} coming from server")
        return jsonify({
            "Message":"Error from server"
        }),500


@session_bp.route('/api/update-session/<int:session_id>', methods=['POST'])
def update_session(session_id):
    try:
        data_session = request.get_json(force=True)

        if not data_session:
            return jsonify({"Message": "No data received"}), 400

        print(f"📋 Received data: {data_session}")

        status, response = update_session_service(data_session, session_id)

        if status:
            return jsonify({
                "Message": "Session updated with success",
                "Response": response
            }), 200
        else:
            return jsonify({
                "Message": "Error in updating session",
                "Response": response
            }), 400

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "Message": f"Error: {e} coming from server"
        }), 500  # ← was missing status code


@session_bp.route('/api/delete-session/<int:session_id>',methods=['POST'])
def delete_session(session_id):
    try:
        status,response = delete_session_service(session_id)
        if status:
            return jsonify(
                response
            ),200
        else:
            return jsonify(
                response
            ),400
    except Exception as e:
        return jsonify({
            "Message":f"Error:{e} in deleting session"
        }),500


@session_bp.route('/api/get-nbr-group-session/<int:session_id>',methods=['GET'])
def get_nbr_group_session(session_id):
    try:
        status,response = get_all_group_session_service(session_id)
        if status:
            print(response)
            return jsonify(response),200
        else:
            return jsonify(response),400

    except Exception as e:
        return jsonify({
            "Message":f"Error:{e} in getting number group session"
        }),500


@session_bp.route('/api/get-nbr-user-session/<int:session_id>',methods=['GET'])
def get_nbr_user_session(session_id):
    try:
        status,response = get_all_user_service(session_id)
        if status:
            return jsonify(response),200
        else:
            return jsonify(response),400
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} in getting number user per session"
        }),500