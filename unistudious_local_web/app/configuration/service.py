import requests
from flask import current_app



def get_account_level_service(account_id):
	try:
		url = f"{current_app.config['BASE_URL']}get_account_level/{account_id}"
		response = requests.get(url,verify=False,timeout=10)
		print(response.json())
		return response.status_code == 200,response
	except Exception as e:
		print(e)
		return False,None