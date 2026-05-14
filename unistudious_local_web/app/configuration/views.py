from flask import Blueprint, render_template, session, redirect, url_for

configuration_view_bp = Blueprint('configuration_view_bp', __name__)


@configuration_view_bp.route('/dashboard/show-level')
def show_level():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_level',
						   account_id=session.get('account_id'))

