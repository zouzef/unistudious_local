from flask import Blueprint, session
from app.utils import render_page, login_required

payment_view_bp = Blueprint('payment_view_bp', __name__)


@payment_view_bp.route('/dashboard/show-payment-session')
def show_payment_session():
    guard = login_required()
    if guard: return guard

    return render_page('show-payment-session',
        account_id=session.get('account_id'),
    )


@payment_view_bp.route('/dashboard/show-payment-session-details/<int:session_id>')
def show_payment_session_details(session_id):
    guard = login_required()
    if guard: return guard

    return render_page('show_payment_session_detail',
        account_id=session.get('account_id'),
        session_id=session_id,
    )


@payment_view_bp.route('/dashboard/show-user-session/<int:id_user>/<int:id_session>')
def show_user_session(id_user, id_session):
    guard = login_required()
    if guard: return guard

    return render_page('show_payment_user_session',
        account_id=session.get('account_id'),
        id_user=id_user,
        id_session=id_session,
    )


@payment_view_bp.route('/dashboard/invoice-payment-session')
def show_invoice_payment():
    guard = login_required()
    if guard: return guard

    return render_page('invoice_session',
        account_id=session.get('account_id'),
    )