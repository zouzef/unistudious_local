from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import requests
import urllib3

# Disable SSL warnings (since you're using verify=False)

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)


# ===============================
# VARIABLES
# ===============================
BASE_URL = " https://172.28.20.178:5004/scl/"



def check_login(username, password):
	payload = {
		"username": username,  # ✅ Correct - string keys
		"password": password  # ✅ Correct - string keys
	}
	url = f"{BASE_URL}authentification-moderateur"

	try:
		response = requests.post(url, json=payload, verify=False, timeout=10)


		if response.status_code == 200:
			return True
		else:
			return False

	except requests.exceptions.RequestException as e:
		print(f"DEBUG: Request failed: {e}")
		return False


@auth_bp.route('/login', methods=['GET'])
def login():
	"""Show login page"""
	return render_template('page-login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
	"""Handle login form submission"""
	data = request.get_json()

	username = data.get('username')
	password = data.get('password')

	# Validate input
	if not username or not password:
		return jsonify({
			'success': False,
			'message': 'Username and password required'
		}), 400

	# Check login
	if check_login(username, password):
		# Store in session
		session['moderator_id'] = username
		session['moderator_name'] = username

		return jsonify({
			'success': True,
			'message': 'Login successful',
			'redirect': '/dashboard'
		})
	else:
		return jsonify({
			'success': False,
			'message': 'Invalid credentials'
		}), 401


@auth_bp.route('/logout')
def logout():
	"""Handle logout"""
	session.clear()
	return redirect('/login')