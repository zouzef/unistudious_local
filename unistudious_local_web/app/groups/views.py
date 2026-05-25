from flask import Blueprint, session
from app.utils import render_page, login_required
from app.session.service import get_locals

groups_view = Blueprint('groups_view', __name__)


@groups_view.route('/dashboard/create-group-user-session/<int:id_session>')
def show_create_group_session(id_session):
    guard = login_required()
    if guard: return guard

    account_id = session.get('account_id')
    local_details = get_locals(account_id)
    local_id = local_details[0].get('id', 1) if local_details else 1

    return render_page('group_user_session',
        account_id=account_id,
        id_session=id_session,
        local_id=local_id,
    )