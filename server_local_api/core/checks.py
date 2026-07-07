from core.repository import find_by_id, exists_by_id


""" -------------------------------- ACCOUNT checks -------------------------------- """
def account_exists(account_id):
	return exists_by_id('account', account_id)


""" -------------------------------- USER checks -------------------------------- """
def user_exists(user_id):
	return exists_by_id('user', user_id)

def virtuel_user_exists(user_id, account_id):
	return exists_by_id('virtual_user',user_id,extra_where="account_id = %s", extra_params=(account_id,))

def get_virtual_user(virtual_id, account_id):
	"""Returns the row so you can pull user_id out of it, or None."""
	return find_by_id('virtual_user', virtual_id, extra_where="account_id = %s", extra_params=(account_id,))



""" -------------------------------- SESSION checks -------------------------------- """
def session_exists(session_id, account_id=None):
	if account_id is not None:
		return exists_by_id('session', session_id, extra_where="account_id = %s", extra_params=(account_id,))
	return exists_by_id('session', session_id)

def relation_user_session_exists(session_id, user_id):
	return exists_by_id(
		'relation_user_session',
		id_value=None,
		extra_where="session_id = %s AND user_id = %s",
		extra_params=(session_id, user_id)
	)
