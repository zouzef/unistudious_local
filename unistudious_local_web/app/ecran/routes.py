# app/ecran/routes.py
from flask import Blueprint, render_template, jsonify

from app.ecran.service import get_ecran_events

# Public, read-only screen: NO login_required, GET only, nothing else is exposed
ecran_bp = Blueprint('ecran', __name__)


@ecran_bp.route('/ecran/<int:account_id>', methods=['GET'])
def show_ecran(account_id):
	"""The calendar page shown on the server screen"""
	return render_template(
		'ecran.html',
		account_id = account_id
	)


@ecran_bp.route('/ecran/data', methods=['GET'])
def api_ecran_data():
	"""Calendar events for the screen (read-only)"""
	events = get_ecran_events()
	response = jsonify({'success': True, 'data': events})
	response.headers['Cache-Control'] = 'no-store'
	return response, 200