# app/session/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
import io
import os
import base64
from app.session.service import (
    get_all_sessions, get_moderator,
    get_locals, get_room, get_teacher,
    get_session_image
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

    return render_template('index.html', page='create-session')


@session_bp.route('/dashboard/show-session-config/<int:id_session>', methods=['GET'])
def show_session_config(id_session):
    """Session configuration page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id', 3)

    return render_template('index.html',
                           id_session=id_session,
                           account_id=account_id,
                           page='session_config')


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