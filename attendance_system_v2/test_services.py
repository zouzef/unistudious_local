# test_attendance.py

from services.auth_service import login_slc
from services.client import FlaskClient
from services.student_service import get_list_students
from services.attendance_service import update_attendance
from detection.recognition import enroll_students, recognize_persons, unenroll_students
import json

with open("configurations.json") as f:
    config = json.load(f)

token  = login_slc(config["slc_config"]["BASE_URL"], config["slc_config"]["MAC"], config["slc_config"]["PASSWORD"])
client = FlaskClient(config["slc_config"]["BASE_URL"], token=token)

CALENDAR_ID = 2107

# STEP 1: Get students
students = get_list_students(client, CALENDAR_ID)
print(f"Students: {students}")

# STEP 2: Enroll students
enroll_students(students)

# STEP 3: Recognize persons
recognized = recognize_persons(CALENDAR_ID)
print(f"Recognized: {recognized}")

# STEP 4: Build map userId → attendance id
attendance_map = {
    str(student.get("userId")): student.get("id")
    for student in students
}
print(f"Attendance map: {attendance_map}")

# STEP 5: Update attendance
for student in students:
    user_id       = str(student.get("userId"))
    attendance_id = attendance_map.get(user_id)
    is_present    = user_id in recognized

    print(f"userId={user_id} → attendance_id={attendance_id} → is_present={is_present}")
    update_attendance(client, attendance_id, is_present)

# STEP 6: Unenroll students
unenroll_students(students)