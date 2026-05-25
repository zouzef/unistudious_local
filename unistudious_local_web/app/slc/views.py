from flask import Blueprint, session
from app.utils import render_page, login_required

slc_view_bp = Blueprint('slc_view', __name__)


@slc_view_bp.route('/dashboard/show-slc')
def show_slc():
    guard = login_required()
    if guard: return guard

    return render_page('show-slc',
        account_id=session.get('account_id'),
    )


@slc_view_bp.route('/dashboard/list-slc-camera')
def show_list_camera():
    guard = login_required()
    if guard: return guard

    return render_page('show-list-camera',
        account_id=session.get('account_id'),
    )


@slc_view_bp.route('/dashboard/list-slc-tablet')
def show_list_tablet():
    guard = login_required()
    if guard: return guard

    return render_page('show-list-tablet',
        account_id=session.get('account_id'),
    )