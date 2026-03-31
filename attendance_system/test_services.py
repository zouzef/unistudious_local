# test_services.py
import json
from services.auth_service import login_slc
from services.client import FlaskClient
from services.attendance_service import update_attendance

with open("configurations.json") as f:
    config = json.load(f)

token = login_slc(
    base_url=config["slc_config"]["BASE_URL"],
    mac=config["slc_config"]["MAC"],
    password=config["slc_config"]["PASSWORD"]
)

client = FlaskClient(base_url=config["slc_config"]["BASE_URL"], token=token)

# Use the real attendance id we saw in the previous test
attendance_id = 9379
result = update_attendance(client, attendance_id, is_present=False)

if result:
    print(f"✅ Attendance {attendance_id} updated successfully.")
else:
    print(f"❌ Failed to update attendance {attendance_id}.")