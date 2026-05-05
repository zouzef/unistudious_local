from flask import Blueprint, render_template, session, redirect, url_for

user_views_bp = Blueprint('user_views',__name__)

# Show the component my_student.html
@user_views_bp.route('/dashboard/my-student')
def show_my_student():
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('index.html', page='my_student', account_id=session.get('account_id'))


# Show the component platform_student.html
@user_views_bp.route('/dashboard/platform_student')
def show_platform_student():
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('index.html', page='platform_student', account_id=session.get('account_id'))


# Show the component show_manager.html
@user_views_bp.route('/dashboard/show-manager')
def show_manager_users():
    if 'moderator_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('index.html',
						   page='show_manager',
						   account_id=session.get('account_id')
						   )


# Show the component view_manager.html
@user_views_bp.route('/dashboard/view-manager/<int:manager_id>')
def show_manager_info(manager_id):
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))
	return render_template('index.html',
						   page='view_manager',
						   account_id= session.get('account_id'),
						   manager_id=manager_id
						   )



# Show the component add_manager
@user_views_bp.route('/dashboard/create-manager')
def create_manager():
	if 'moderator_id' not in session:
		return redirect(url_for('auth.login_page'))
	return render_template('index.html',
						   page='create_manager',
						   account_id=session.get('account_id')
						   )
