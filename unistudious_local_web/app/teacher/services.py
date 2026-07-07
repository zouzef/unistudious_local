# app/teacher/service.py
import requests
from flask import current_app


# ── CREATE Teacher Service  ──────────────────────────────────────────────────────────
def create_teacher_service(account_id: int, form_items: list, files: dict) -> tuple:
    url = f"{current_app.config['BASE_URL']}create_teacher/{account_id}"
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
        print(f"Error: {e} coming from create_teacher_service")
        return False, None


# ── Get Teacher Info Service  ──────────────────────────────────────────────────────────
def get_all_teacher_service() -> tuple:
    url=f"{current_app.config['BASE_URL']}get_all_teachers"
    try:
        response = requests.get(url,verify=False,timeout=10)
        if response.status_code == 200:
            return True,response.json()
        else:
            return False,response.json()
    except Exception as e:
        print(f"Error: {e} coming from server")
        return False,None