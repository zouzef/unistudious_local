from flask import Blueprint, render_template, session, redirect, url_for

payment_view_bp = Blueprint('payment_view_bp', __name__)

@payment_view_bp.route('/dashboard/show-payment-session')
def show_payment_session():
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('index.html',
                      page='show-payment-session',
                      account_id=session.get('account_id'))  # ✅ added


@payment_view_bp.route('/dashboard/show-payment-session-details/<int:session_id>')
def show_payment_session_details(session_id):
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('index.html',
                      session_id=session_id,
                      page='show_payment_session_detail',
                      account_id=session.get('account_id'))  # ✅ added


@payment_view_bp.route('/dashboard/show-user-session/<int:id_user>/<int:id_session>')
def show_user_session(id_user, id_session):
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login'))
    print("User_id: ",id_user)
    print("Session_id",id_session)
    return render_template('index.html',
                      id_user=id_user,
                      id_session=id_session,
                      page='show_payment_user_session',
                      account_id=session.get('account_id'))  # ✅ added


@payment_view_bp.route('/dashboard/invoice-payment-session')
def show_invoice_payment():
    if not 'moderator_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html',
                           account_id=session.get('account_id'),
                           page ='invoice_session'
                           )