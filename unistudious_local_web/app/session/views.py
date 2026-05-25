from flask import Blueprint, session
from app.utils import render_page, login_required
from app.session.service import (
    get_all_sessions,
    get_moderator,
    get_locals
)

session_view_bp = Blueprint('session_views', __name__)


# ─── Routes ──────────────────────────────────────────────────────────────────

@session_view_bp.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    guard = login_required()
    if guard: return guard

    account_id = session.get('account_id')

    return render_page('home',
        sessions=get_all_sessions(account_id),
        data_modera=get_moderator(account_id),
        local_details=get_locals(account_id),
        account_id=account_id,
    )


@session_view_bp.route('/dashboard/show-session')
def show_sessions():
    """Display all sessions page"""
    guard = login_required()
    if guard: return guard

    account_id = session.get('account_id')

    return render_page('show-session',
        sessions=get_all_sessions(account_id),
        account_id=account_id,
    )


@session_view_bp.route('/dashboard/create-session')
def create_session():
    """Create new session page"""
    guard = login_required()
    if guard: return guard

    return render_page('create-session',
        account_id=session.get('account_id'),
    )


@session_view_bp.route('/dashboard/view-session/<int:session_id>')
def view_session(session_id):
    """Update session page"""
    guard = login_required()
    if guard: return guard

    return render_page('view_session',
        account_id=session.get('account_id'),
        session_id=session_id,
    )


@session_view_bp.route('/dashboard/show-session-config/<int:id_session>')
def show_sessions_config(id_session):
    """Session configuration page"""
    guard = login_required()
    if guard: return guard

    from app.calendar.service import get_calendar_per_session

    account_id = session.get('account_id')

    return render_page('session_config',
        id_session=id_session,
        account_id=account_id,
        local_details=get_locals(account_id),
        sessions=get_all_sessions(account_id),
        data_modera=get_moderator(account_id),
        calendar_data=get_calendar_per_session(account_id, id_session),
    )


@session_view_bp.route('/dashboard/show-all-user-session/<int:id_session>')
def show_user_session(id_session):
    """Show all users in a session"""
    guard = login_required()
    if guard: return guard

    return render_page('show_user_session',
        id_session=id_session,
        account_id=session.get('account_id'),
    )