# app/groups/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.groups.service import (
    get_groups,
    delete_group,
    delete_user_from_group,
    get_users_not_affected,
    affect_user,
    get_subject_group,
    create_group
)
from app.session.service import get_locals

groups_bp = Blueprint('groups', __name__)


# ==========================================
# PAGE ROUTES
# ==========================================

@groups_bp.route('/dashboard/create-group-user-session/<int:id_session>')
def show_create_group_session(id_session):
    """Create/edit group for session page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id', 3)

    local_details = get_locals(account_id)
    local_id = local_details[0].get('id', 1) if local_details else 1

    return render_template('index.html',
                           id_session=id_session,
                           account_id=account_id,
                           local_id=local_id,
                           page='group_user_session')


# ==========================================
# API ROUTES
# ==========================================

@groups_bp.route('/api/get-group/<int:session_id>/<int:account_id>')
def api_get_groups(session_id, account_id):
    """Get groups with students"""
    result = get_groups(account_id, session_id)
    return jsonify({"Message": "Success", "data": result}), 200


@groups_bp.route('/api/delete-group/<int:group_id>', methods=['DELETE'])
def api_delete_group(group_id):
    """Delete a group"""
    success, message = delete_group(group_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 404


@groups_bp.route('/api/delete_user_f_group/<int:session_id>/<int:user_id>', methods=['POST'])
def api_delete_user_from_group(session_id, user_id):
    """Delete user from group"""
    success, message = delete_user_from_group(session_id, user_id)
    if success:
        return jsonify({"Message": message}), 200
    return jsonify({"Message": message}), 400


@groups_bp.route('/api/show_user_not_affected/<int:session_id>/<int:account_id>')
def api_get_users_not_affected(session_id, account_id):
    """Get users not affected to any group"""
    result = get_users_not_affected(session_id, account_id)
    return jsonify({"Message": "Success", "students": result}), 200


@groups_bp.route('/api/affect_user/<int:session_id>', methods=['POST'])
def api_affect_user(session_id):
    """Affect user to a group"""
    data = request.get_json()

    if not data:
        return jsonify({"Message": "No data provided"}), 400

    user_id = data.get('user_id')
    group_id = data.get('group_id')

    if not user_id or not group_id:
        return jsonify({"Message": "Missing user_id or group_id"}), 400

    success, result = affect_user(session_id, user_id, group_id)
    if success:
        return jsonify({"Message": "Success", "data": result}), 200
    return jsonify({"Message": result}), 400


@groups_bp.route('/api/get_subject_group/<int:account_id>', methods=['GET'])
def api_get_subject_group(account_id):
    """Get subjects for account"""
    result = get_subject_group(account_id)
    return jsonify(result), 200


@groups_bp.route('/api/create_group/<int:session_id>', methods=['POST'])
def api_create_group(session_id):
    """Create a new group"""
    data = request.get_json()

    if not data:
        return jsonify({"Message": "No data provided"}), 400

    result, status_code = create_group(session_id, data)
    return jsonify(result), status_code