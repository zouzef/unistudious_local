from services.auth_service import login_slc
from services.client import FlaskClient
from services.student_service import get_list_students
from detection.recognition import enroll_students, recognize_persons
import json

with open("configurations.json") as f:
    config = json.load(f)

token  = login_slc(config["slc_config"]["BASE_URL"], config["slc_config"]["MAC"], config["slc_config"]["PASSWORD"])
client = FlaskClient(config["slc_config"]["BASE_URL"], token=token)

students = get_list_students(client, 2107)
enroll_students(students)

# ✅ TEST RECOGNITION
results = recognize_persons(2107)
if results:
    for i in results:
        print(f"student: {i} is present")
else:
    print("There is no student present")
print("Recognition results:", results)