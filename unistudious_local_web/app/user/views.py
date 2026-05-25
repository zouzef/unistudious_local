from flask import Blueprint, session
from app.utils import render_page, login_required

user_views_bp = Blueprint('user_views', __name__)


# ========================================= STUDENT =========================================

@user_views_bp.route('/dashboard/my-student')
def show_my_student_view():
    guard = login_required()
    if guard: return guard

    return render_page('my_student',
        account_id=session.get('account_id'),
    )


@user_views_bp.route('/dashboard/platform_student')
def show_platform_student_view():
    guard = login_required()
    if guard: return guard

    return render_page('platform_student',
        account_id=session.get('account_id'),
    )


# ========================================= MANAGER =========================================

@user_views_bp.route('/dashboard/show-manager')
def show_manager_users_view():
    guard = login_required()
    if guard: return guard

    return render_page('show_manager',
        account_id=session.get('account_id'),
    )


@user_views_bp.route('/dashboard/view-manager/<int:manager_id>')
def show_manager_info_view(manager_id):
    guard = login_required()
    if guard: return guard

    return render_page('view_manager',
        account_id=session.get('account_id'),
        manager_id=manager_id,
    )


@user_views_bp.route('/dashboard/create-manager')
def create_manager_view():
    guard = login_required()
    if guard: return guard

    return render_page('create_manager',
        account_id=session.get('account_id'),
    )


@user_views_bp.route('/dashboard/view-profile')
def view_profile():
    guard = login_required()
    if guard: return guard
    print(session.get('user_id'))
    return render_page('view_profile',
                       account_id = session.get('account_id'),
                       user_id = session.get('user_id')
                       )


@user_views_bp.route('/dashboard/view-account-setting')
def view_account_setting():
    guard = login_required()
    if guard: return guard
    return render_page('view_account_setting',
                       account_id = session.get('account_id'),
                       )
# ========================================= TEACHER =========================================

@user_views_bp.route('/dashboard/show-teacher')
def show_teacher_view():
    guard = login_required()
    if guard: return guard

    return render_page('show_teacher',
        account_id=session.get('account_id'),
    )


@user_views_bp.route('/dashboard/create-teacher')
def create_teacher_view():
    guard = login_required()
    if guard: return guard

    return render_page('create_teacher',
        account_id=session.get('account_id'),
    )


