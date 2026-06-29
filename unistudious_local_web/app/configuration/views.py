from flask import Blueprint, render_template, session, redirect, url_for
from app.utils import render_page, login_required

configuration_view_bp = Blueprint('configuration_view_bp', __name__)


# =========================================== LEVEL VIEWS ===========================================

@configuration_view_bp.route('/dashboard/show-level')
def show_level():
    guard = login_required()
    if guard: return guard

    return render_page('show_level',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-level')
def create_level():
    guard = login_required()
    if guard: return guard

    return render_page('create_level',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/view-level/<int:account_level>')
def view_level(account_level):
    guard = login_required()
    if guard: return guard

    return render_page('view_level',
        account_id=session.get('account_id'),
        account_level=account_level)


# =========================================== SECTION ===========================================

@configuration_view_bp.route('/dashboard/show-section')
def show_section():
    guard = login_required()
    if guard: return guard

    return render_page('show_section',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-section')
def create_section():
    guard = login_required()
    if guard: return guard

    return render_page('create_section',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/view-section/<int:account_section_id>')
def viw_section(account_section_id):
    guard = login_required()
    if guard: return guard

    return render_page('view_section',
        account_id=session.get('account_id'),
        account_section_id=account_section_id)


# =========================================== SUBJECTS ===========================================

@configuration_view_bp.route('/dashboard/show-subject')
def show_subject():
    guard = login_required()
    if guard: return guard

    return render_page('show_subject',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-subject')
def create_subject():
    guard = login_required()
    if guard: return guard

    return render_page('create_subject',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/view_subject/<int:subject_id>')
def view_subject(subject_id):
    guard = login_required()
    if guard: return guard

    return render_page('view_subject',
        account_id=session.get('account_id'),
        subject_id=subject_id)


# =========================================== FORMATION ===========================================

@configuration_view_bp.route('/dashboard/show-formation')
def show_formation():
    guard = login_required()
    if guard: return guard

    return render_page('show_formation',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-formation')
def create_formation():
    guard = login_required()
    if guard: return guard

    return render_page('create_formation',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/view_formation/<int:formation_id>')
def view_formation(formation_id):
    guard = login_required()
    if guard: return guard

    return render_page('view_formation',
        account_id=session.get('account_id'),
        formation_id=formation_id)


# =========================================== TAGS ===========================================

@configuration_view_bp.route('/dashboard/show-tag')
def show_tag():
    guard = login_required()
    if guard: return guard

    return render_page('show_tag',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-tag')
def create_tage():
    guard = login_required()
    if guard: return guard

    return render_page('create_tag',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/view-account-tag/<int:tag_id>')
def view_tag(tag_id):
    guard = login_required()
    if guard: return guard

    return render_page('view_tag',
        account_id=session.get('account_id'),
        tag_id=tag_id)


# =========================================== COMPLETION TAGS ===========================================

@configuration_view_bp.route('/dashboard/show-completion-tag')
def show_completion_tag():
    guard = login_required()
    if guard: return guard

    return render_page('show_completion_tag',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/create-completion-tag')
def create_completion_tag():
    guard = login_required()
    if guard: return guard

    return render_page('create_completion_tag',
        account_id=session.get('account_id'))


@configuration_view_bp.route('/dashboard/view-completion-tag/<int:completionTag_id>')
def view_completion_tag(completionTag_id):
    guard = login_required()
    if guard: return guard

    return render_page('view_completion_tag',
        account_id=session.get('account_id'),
        completionTag_id=completionTag_id)



# =========================================== SLC DOOR ===========================================
@configuration_view_bp.route('/dashboard/list-slc-door')
def show_slc_door():
    guard = login_required()
    if guard: return guard

    return render_page('show_slc_door',
        account_id=session.get('account_id'))
