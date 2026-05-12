from flask import Blueprint, render_template, session, redirect, url_for
from app.session.service import(
	get_all_sessions,
	get_moderator,
	get_locals
)


session_view_bp = Blueprint('session_views',__name__)


@session_view_bp.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id')

    return render_template('index.html',
                           sessions=get_all_sessions(account_id),
                           data_modera=get_moderator(account_id),
                           local_details=get_locals(account_id),
                           account_id=account_id,
                           page='home')


@session_view_bp.route('/dashboard/show-session')
def show_sessions():
    """Display all sessions page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))

    account_id = session.get('account_id')

    return render_template('index.html',
                           sessions=get_all_sessions(account_id),

                           account_id=account_id,
                           page='show-session')


@session_view_bp.route('/dashboard/create-session')
def create_session():
    """Create new session page"""
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    account_id = session.get('account_id', 3)
    return render_template('index.html',
                           account_id=account_id,
                           page='create-session')


@session_view_bp.route('/dashboard/view-session/<int:session_id>')
def view_session(session_id):
	"""Update session page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))
	account_id = session.get('account_id', 3)
	return render_template('index.html',
						   account_id=account_id,
						   page='view_session')


@session_view_bp.route('/dashboard/show-session-config/<int:id_session>')
def show_sessions_config(id_session):
	"""Session configuration page"""
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))

	account_id = session.get('account_id', 3)

	from app.session.service import get_locals, get_all_sessions, get_moderator
	from app.calendar.service import get_calendar_per_session

	return render_template('index.html',
						   id_session=id_session,
						   account_id=account_id,
						   local_details=get_locals(account_id),
						   sessions=get_all_sessions(account_id),
						   data_modera=get_moderator(account_id),
						   calendar_data=get_calendar_per_session(account_id, id_session),
						   page='session_config')


@session_view_bp.route('/dashboard/show-all-user-session/<int:id_session>')
def show_user_session(id_session):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))
	return render_template('index.html',
						   id_session=id_session,
						   account_id=session.get('account_id'),
						   page='show_user_session')