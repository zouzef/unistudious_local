# app/manager/service.py
import requests
from flask import current_app

# ── Get Manager info Service ─────────────────────────────────────────────────────────────
def get_manager_info_service() -> tuple:
    url=f"{current_app.config['BASE_URL']}get-manager-info"
    try:
        response=requests.get(url,verify=False)
        if response.status_code==200:
            return True,response.json()
        else:
            return False,response.json()
    except Exception as e:
        print(e)
        return False,None


# ── Create Manager Service ─────────────────────────────────────────────────────────────
def create_manager_service(account_id: int, form_items: list, files: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_manager/{account_id}"
    try:
        upload_files = {}
        image_file = files.get("image")
        if image_file and image_file.filename:
            upload_files["image"] = (
                image_file.filename,
                image_file.stream,
                image_file.mimetype
            )

        response = requests.post(
            url,
            data=form_items,
            files=upload_files if upload_files else None,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()

    except Exception as e:
        print(f"Error: {e} coming from create_manager_service")
        return False, None

# ── Update Manager Service ─────────────────────────────────────────────────────────────
def update_manager_service(manager_id: int, form_items: list, files: dict) -> tuple:
	url = f"{current_app.config['BASE_URL']}update_manager/{manager_id}"
	try:
		upload_files = {}
		image_file = files.get("image")
		if image_file and image_file.filename:
			upload_files["image"] = (
				image_file.filename,
				image_file.stream,
				image_file.mimetype
			)
		response = requests.post(
			url,
			data    = form_items,
			files   = upload_files if upload_files else None,
			verify  = False,
			timeout = 10
		)
		return response.status_code == 200, response.json()

	except Exception as e:
		print(f"Error: {e} coming from update_manager_service")
		return False, None