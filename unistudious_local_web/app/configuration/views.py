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
						   account_section_id=account_section_id,
						   account_id = session.get('account_id'))

# ========================================= SUBJECTS =========================================

@configuration_view_bp.route('/dashboard/show-subject')
def show_subject():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_subject',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/create-subject')
def create_subject():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create_subject',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/view_subject/<int:subject_id>')
def view_subject(subject_id):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='view_subject',
						   subject_id = subject_id,
						   account_id = session.get('account_id'))


# ========================================= FORMATION =========================================
@configuration_view_bp.route('/dashboard/show-formation')
def show_formation():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_formation',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/create-formation')
def create_formation():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create_formation',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/view_formation/<int:formation_id>')
def view_formation(formation_id):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='view_formation',
						   formation_id = formation_id,
						   account_id = session.get('account_id'))



# ========================================= TAGS =========================================
@configuration_view_bp.route('/dashboard/show-tag')
def show_tag():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_tag',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/create-tag')
def create_tage():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create_tag',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/view-tag/<int:tag_id>')
def view_tag(tag_id):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='view_tag',
						   tag_id = tag_id,
						   account_id= session.get('account_id'))


# =========================================COMPLETION TAGS =========================================
@configuration_view_bp.route('/dashboard/show-completion-tag')
def show_completion_tag():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='show_completion_tag',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/create-completion-tag')
def create_completion_tag():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='create_completion_tag',
						   account_id = session.get('account_id'))

@configuration_view_bp.route('/dashboard/view-completion-tag/<int:completionTag_id>')
def view_completion_tag(completionTag_id):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login'))

	return render_template('index.html',
						   page='view_completion_tag',
						   completionTag_id = completionTag_id,
						   account_id= session.get('account_id'))