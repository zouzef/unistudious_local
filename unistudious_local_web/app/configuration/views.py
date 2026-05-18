from flask import Blueprint, render_template, session, redirect, url_for

configuration_view_bp = Blueprint('configuration_view_bp', __name__)



#=========================================== LEVEL VIEWS ===========================================
@configuration_view_bp.route('/dashboard/show-level')
def show_level():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_level',
						   account_id=session.get('account_id'))

@configuration_view_bp.route('/dashboard/create-level')
def create_level():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create_level',
						   account_id=session.get('account_id'))

@configuration_view_bp.route('/dashboard/view-level/<int:account_level>')
def view_level(account_level):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='view_level',
						   account_id=session.get('account_id'),
						   account_level=account_level)


#=========================================== ACCOUNT SECTION ===========================================

@configuration_view_bp.route('/dashboard/show-section')
def show_section():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_section',
						   account_id = session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-section')
def create_section():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create_section',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/view-section/<int:account_section_id>')
def viw_section(account_section_id):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='view_section',
						   account_id = session.get('account_id'))