from flask import Blueprint, render_template, session, redirect, url_for


slc_view_bp = Blueprint('slc_view', __name__)

@slc_view_bp.route('/dashboard/show-slc')
def show_slc():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))

	account_id = session.get('account_id')
	return render_template('index.html',
						  account_id=account_id,
						  page='show-slc')


@slc_view_bp.route('/dashboard/list-slc-camera')
def show_list_camera():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))

	account_id = session.get('account_id')

	return render_template('index.html',
						   account_id=account_id,
						   page='show-list-camera')


@slc_view_bp.route('/dashboard/list-slc-tablet')
def show_list_tablet():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))

	account_id = session.get('account_id')
	return render_template('index.html',
						   account_id=account_id,
						   page='show-list-tablet')