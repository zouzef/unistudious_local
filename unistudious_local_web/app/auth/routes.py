# app/auth/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect
from app.auth.service import login

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Show login page"""
    return render_template('page-login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission"""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    success, user_data, message = login(username, password)

    if success:
        session.permanent = True
        session['moderator_id'] = user_data['username']
        session['moderator_name'] = user_data['username']
        session['user_id'] = user_data['user_id']
        session['account_id'] = user_data['account_id']

        return jsonify({
            'success': True,
            'message': message,
            'redirect': '/dashboard'
        })
    else:
        return jsonify({
            'success': False,
            'message': message
        }), 401


@auth_bp.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    return redirect('/login')