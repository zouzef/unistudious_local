from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import requests
import urllib3

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# ===============================
# VARIABLES
# ===============================
BASE_URL = " https://172.28.20.178:5004/scl/"


def check_login(username, password):
	payload = {
		"username": username,
		"password": password
	}
	url = f"{BASE_URL}authentification-moderateur"

	try:
		response = requests.post(url, json=payload, verify=False, timeout=10)

		if response.status_code == 200:
			data = response.json()
			print(f"✅ Login successful, account_id: {data.get('account_id')}")  # ← DEBUG
			return True, data.get('account_id', 3)
		else:
			print(f"❌ Login failed, status: {response.status_code}")  # ← DEBUG
			return False, None

	except requests.exceptions.RequestException as e:
		print(f"❌ Request failed: {e}")
		return False, None


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

	if not username or not password:
		return jsonify({
			'success': False,
			'message': 'Username and password required'
		}), 400

	# Get login result and account_id
	success, account_id = check_login(username, password)

	if success:
		session.permanent = True
		session['moderator_id'] = username
		session['moderator_name'] = username
		session['account_id'] = account_id

		# ← ADD DEBUG LOGGING
		print(f"✅ Session set: moderator_id={username}, account_id={account_id}")
		print(f"✅ Session contents: {dict(session)}")

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