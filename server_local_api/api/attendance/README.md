# Attendance API

Base URL: `/scl`

All endpoints require authentication token in header:
```
Authorization: Bearer <token>
```

## Endpoints

### 1. Get Attendance by Calendar
**GET** `/scl/get-attendance/<calendar_id>`

Get all attendance records for a specific calendar.

**Response (200):**
```json
{
  "attendance": [
    {
      "id": 1,
      "userName": "John Doe",
      "userId": 123,
      "userRefRlc": "REF123",
      "session": 456,
      "account": 789,
      "group": 10,
      "isPresent": true,
      "day": "2026-01-20",
      "calander": 1,
      "note": "Late",
      "updatedAt": "2026-01-20 10:30:00"
    }
  ]
}
```

---

### 2. Get Student Groups for Attendance
**GET** `/scl/attendance-get-group-student-select/<calendarId>/<userId>`

Get all groups a student belongs to for a specific calendar.

**Response (200):**
```json
{
  "groups": [
    {
      "relationId": 78,
      "id": 5,
      "name": "Group A"
    }
  ]
}
```

---

### 3. Save Student Attendance
**POST** `/scl/attendance-save-user`

Mark a student present with optional group assignment.

**Request Body:**
```json
{
  "userId": 123,
  "calendarId": 456,
  "addToGroup": false,
  "joinToGroup": false,
  "selectedGroupId": null,
  "relationId": null
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Student attendance added successfully",
  "attendance_id": 789
}
```

---

### 4. Get Attendance Statistics
**GET** `/scl/attendance-statistics/<id_calender>`

Get present/absent/total counts for a calendar.

**Response (200):**
```json
{
  "present_count": 25,
  "absent_count": 5,
  "total_count": 30
}
```

---

### 5. Delete Attendance by Calendar + User
**DELETE** `/scl/delete_attendance_api/<calender_id>/<user_id>`

Soft delete attendance for a specific user in a calendar.

**Response (200):**
```json
{
  "status": "ok",
  "message": "Attendance deleted successfully"
}
```

---

### 6. Delete Attendance by ID
**DELETE** `/scl/attendance-delete-student/<id_attendance>`

Soft delete a specific attendance record by ID.

**Response (200):**
```json
{
  "message": "Attendance record deleted successfully"
}
```

---

### 7. Get List of Students to Add
**GET** `/scl/list-add-student-attendance/<calender_id>`

Get students who can be added to attendance (not yet marked).

**Response (200):**
```json
{
  "users": [
    {
      "id": 123,
      "fullName": "Jane Smith",
      "relationId": 456,
      "calendarId": 789,
      "groupId": 1
    }
  ]
}
```

---

### 8. Get Next Attendance Session
**GET** `/scl/get-next-attendance/<calendarId>`

Get the next calendar session after the given one.

**Response (200):**
```json
{
  "message": "Success",
  "reference_calendar_id": 123,
  "next_calendar": {
    "id": 124,
    "name": "Math Class",
    "start_time": "2026-01-21 10:00:00",
    "end_time": "2026-01-21 12:00:00",
    "description": "Advanced Math"
  }
}
```

---

### 9. Get Next Single Attendance
**GET** `/scl/get-next-single-attendance/<calendarId>`

Alternative endpoint for getting next session.

---

### 10. Get All Future Attendances (v2)
**GET** `/scl/get-next-attendance-v2/<calendarId>`

Get all future calendar sessions after the given one.

**Response (200):**
```json
{
  "message": "Success",
  "total_future_calendars": 5,
  "calendars": [...]
}
```

---

### 11. Reset Attendance
**POST** `/scl/reset_attendance/<calender_id>`

Reset all attendance for a calendar (set all to absent, clear notes).

**Response (200):**
```json
{
  "status": "ok",
  "message": "Reset successfully"
}
```

---

### 12. Get Static Attendance Counts
**GET** `/scl/static_attendance/<calander_id>`

Get distinct present/absent counts.

**Response (200):**
```json
{
  "status": "ok",
  "data": {
    "present": 20,
    "absent": 10
  }
}
```

---

### 13. Update Attendance Status
**POST** `/scl/update-attendance-student/<id_attendance>`

Update attendance status (present/absent).

**Request Body:**
```json
{
  "status": true
}
```

**Response (200):**
```json
{
  "message": "Attendance status updated successfully",
  "attendance_id": 123,
  "status": true
}
```

---

### 14. Update Attendance Note
**POST** `/scl/update-attendance-note/<attendanceId>`

Add or update a note for an attendance record.

**Request Body:**
```json
{
  "note": "Arrived late due to traffic"
}
```

**Response (200):**
```json
{
  "message": "Attendance note updated successfully",
  "attendance_id": 123,
  "note": "Arrived late due to traffic"
}
```