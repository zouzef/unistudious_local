from flask import Blueprint, session
from app.utils import render_page, login_required
from app.attendance.service import get_attendance_page_data

attendance_view = Blueprint('attendance_view', __name__)


@attendance_view.route('/dashboard/show-attendance-sessions/<int:session_id>')
def show_attendance_page(session_id):
    guard = login_required()
    if guard: return guard

    return render_page('attendance_page',
        account_id=session.get('account_id'),
        id_session=session_id,
    )


@attendance_view.route('/dashboard/show-attendance-presence/<int:calendar_id>')
def show_attendance_presence(calendar_id):
    guard = login_required()
    if guard: return guard

    data = get_attendance_page_data(calendar_id)

    return render_page('show_attendance_presence',
        account_id=session.get('account_id'),
        id_calander=calendar_id,
        **data,
    )


@attendance_view.route('/dashboard/show-attendance-unknown-student/<int:calendar_id>')
def show_attendance_unknown(calendar_id):
    guard = login_required()
    if guard: return guard

    return render_page('show-unknown-student',
        account_id=session.get('account_id'),
        calender_id=calendar_id,
    )