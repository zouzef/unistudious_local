# app/utils/__init__.py

from flask import render_template, session, redirect, url_for

PAGE_TEMPLATES = {
    'home':                        'home_page.html',
    'session_config':              'session_view/session_config.html',
    'attendance_page':             'calendar_view/attendance_page.html',
    'group_user_session':          'user_view/group_config.html',
    'session_calander':            'session_view/session_calander.html',
    'show-session':                'session_view/show_session.html',
    'show_user_session':           'session_view/show_user_session.html',
    'show-payment-session':        'payment_view/show_payment_session.html',
    'show_payment_session_detail': 'payment_view/show_payment_session_detail.html',
    'show_payment_user_session':   'payment_view/show_payment_user.html',
    'invoice_session':             'payment_view/invoice-payment-session.html',
    'show_attendance_presence':    'calendar_view/show_attendance_presence.html',
    'create-session':              'session_view/create_session.html',
    'show-slc':                    'settingServer_view/show_slc.html',
    'show-list-camera':            'settingServer_view/list_camera.html',
    'show-list-tablet':            'settingServer_view/list_tablet.html',
    'show-unknown-student':        'calendar_view/show_unknown_student.html',
    'calander_request_page':       'calendar_view/calander_request_page.html',
    'my_student':                  'user_view/my_student.html',
    'platform_student':            'user_view/platform_student.html',
    'view_session':                'session_view/view_session.html',
    'show_manager':                'manager_view/show_manager.html',
    'view_manager':                'manager_view/view_manager.html',
    'create_manager':              'manager_view/create_manager.html',
    'show_teacher':                'teacher_view/show_teacher.html',
    'create_teacher':              'teacher_view/create_teacher.html',
    'show_level':                  'configuration/levels/show_level.html',
    'create_level':                'configuration/levels/create-level.html',
    'view_level':                  'configuration/levels/view_level.html',
    'show_section':                'configuration/section/show_section.html',
    'create_section':              'configuration/section/create_section.html',
    'view_section':                'configuration/section/view_section.html',
    'show_subject':                'configuration/subject/show_subject.html',
    'create_subject':              'configuration/subject/create_subject.html',
    'view_subject':                'configuration/subject/view_subject.html',
    'show_formation':              'configuration/formation/show_formation.html',
    'create_formation':            'configuration/formation/create_formation.html',
    'view_formation':              'configuration/formation/view_formation.html',
    'show_tag':                    'configuration/tags/show_tag.html',
    'create_tag':                  'configuration/tags/create_tag.html',
    'view_tag':                    'configuration/tags/view_tag.html',
    'show_completion_tag':         'configuration/completion_tag/show_completion_tag.html',
    'create_completion_tag':       'configuration/completion_tag/create_completion_tag.html',
    'view_completion_tag':         'configuration/completion_tag/view_completion_tag.html',
}


def render_page(page, **kwargs):
    return render_template(
        'index.html',
        page=page,
        page_template=PAGE_TEMPLATES.get(page, '404.html'),
        **kwargs
    )


def login_required():
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    return None


# ↓ whatever was already in this file stays below here ↓