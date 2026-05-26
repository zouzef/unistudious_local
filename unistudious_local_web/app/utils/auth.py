from flask import session

def auth_headers() -> dict:
	"""
		Build the Authorization header from te token stored in the session.
		Every service function that calls the local API server uses this
	:return:
	"""
	token = session.get("access_token", "")
	return {"Authorization": f"Bearer {token}"}
