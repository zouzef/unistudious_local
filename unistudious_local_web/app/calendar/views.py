from flask import Blueprint, session
from app.utils import render_page, login_required

calendar_view = Blueprint('calendar_view', __name__)


@calendar_view.route('/dashboard/create-session-calendar/<int:id_session>')
def show_create_session_calendar(id_session):
    guard = login_required()
    if guard: return guard

    return render_page('session_calander',
        account_id=session.get('account_id'),
        id_session=id_session,
    )


@calendar_view.route('/dashboard/show-calander-request/<int:account_id>')
def show_calendar_request(account_id):
    guard = login_required()
    if guard: return guard

    return render_page('calander_request_page',
        account_id=account_id,
    )