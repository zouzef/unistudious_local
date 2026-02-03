# Calendar API

Base URL: `/scl`

Authentication required for all endpoints.

## Endpoints

### 1. Delete Calendar Interval
**POST** `/scl/deleting_interval/<session_id>`

Soft delete calendars within a time range.

**Request Body:**
```json
{
  "start_date": "2026-01-20 10:00:00",
  "end_date": "2026-01-25 18:00:00"
}
```

**Response (200):**
```json
{
  "message": "success",
  "data": [...]
}
```

---

### 2. Get Calendar by ID
**GET** `/scl/get_calander_id/<id_calender>`

Get a specific calendar by ID.

**Response (200):**
```json
{
  "message": "Success",
  "data": {
    "id": 123,
    "title": "Math Class",
    "start_time": "2026-01-20 10:00:00",
    ...
  }
}
```

---

### 3. Get Group from Calendar
**GET** `/scl/get-group-calender/<calendarId>`

Get the group ID associated with a calendar.

**Response (200):**
```json
{
  "group_session_id": 5
}
```

---

### 4. Get Next Session
**GET** `/scl/get_next_session/<calendarId>`

Get the next calendar session after the current one.

**Response (200):**
```json
{
  "data": {
    "id": 124,
    "start_time": "2026-01-21 10:00:00"
  }
}
```

---

### 5. Get All Today's Calendars
**GET** `/scl/get-all-calender`

Get all calendar sessions for today.

**Response (200):**
```json
{
  "data": [
    {
      "id": 123,
      "name": "Math Class",
      "start": "2026-01-20 10:00:00",
      "teacherFullName": "Dr. Smith",
      "subjectName": "Mathematics",
      ...
    }
  ]
}
```

---

### 6. Get Account Data by Calendar
**GET** `/scl/data_account/<id>`

Get account information for a calendar.

**Response (200):**
```json
{
  "status": "ok",
  "data": [...]
}
```

---

### 7. Get Calendar by Session and Account
**GET** `/scl/get_calendar_session/<id_session>/<id_account>`

Get calendars filtered by session and account.

**Response (200):**
```json
{
  "message": "Success",
  "data": [...]
}
```


---

### 8. Create Calendar Entry
**POST** `/scl/create_calender`

Create a new calendar entry (session/class) with conflict validation.

**Request Body:**
```json
{
  "session_id": 1,
  "account_id": 1,
  "local_id": 1,
  "group_id": 5,
  "room_id": 3,
  "teacher_id": 10,
  "subject_id": 7,
  "description": "Math class for beginners",
  "start_time": "2026-01-29 09:00:00",
  "end_time": "2026-01-29 11:00:00",
  "title": "Introduction to Algebra",
  "type": "lecture"
}
```

**Required Fields:**
- `session_id` (int): Session ID
- `account_id` (int): Account ID
- `local_id` (int): Local/building ID
- `group_id` (int): Group ID
- `room_id` (int): Room ID
- `teacher_id` (int): Teacher user ID
- `subject_id` (int): Subject ID
- `description` (string): Class description
- `start_time` (string): Start datetime (format: "YYYY-MM-DD HH:MM:SS")
- `end_time` (string): End datetime (format: "YYYY-MM-DD HH:MM:SS")
- `title` (string): Session title
- `type` (string): Session type (e.g., "lecture", "lab", "seminar")

**Process:**
1. Validates all required fields are present and non-empty
2. Checks for **room conflicts** - ensures room is not double-booked
3. Checks for **group conflicts** - ensures group doesn't have overlapping sessions
4. Checks for **teacher conflicts** - ensures teacher is available
5. Generates a unique color for calendar display
6. Creates auto-generated reference ID
7. Inserts calendar entry into database

**Conflict Checks:**

**Room Conflict:**
- Same room on the same date with overlapping time slots
- Status code: 402

**Group Conflict:**
- Same group on the same date with overlapping time slots
- Status code: 402

**Teacher Conflict:**
- Same teacher on the same date with overlapping time slots
- Status code: 402

**Response (201) - Success:**
```json
{
  "Message": "Calendar entry created successfully",
  "calander_id": 123,
  "ref": "group-51137-456",
  "color": "#A3C2F1"
}
```

**Response (400) - Missing Fields:**
```json
{
  "Message": "Missing required fields",
  "missing_fields": ["teacher_id", "room_id"]
}
```

**Response (400) - Empty Fields:**
```json
{
  "Message": "Fields cannot be empty",
  "empty_fields": ["description", "title"]
}
```

**Response (402) - Room Conflict:**
```json
{
  "Message": "Room already reserved!",
  "Error": "Room-Conflict"
}
```

**Response (402) - Group Conflict:**
```json
{
  "Message": "Group not available in this time",
  "Error": "Group-Conflict"
}
```

**Response (402) - Teacher Conflict:**
```json
{
  "Message": "Teacher not available in this time",
  "Error": "Teacher-Conflict"
}
```

**Response (402) - Color Generation Failed:**
```json
{
  "Message": "Could not find unique color",
  "Error": "Warning: Could not find unique color after 50 attempts"
}
```

**Response (500) - Server Error:**
```json
{
  "Message": "Internal Server Error",
  "error": "error description"
}
```

**Field Descriptions:**
- `calander_id`: Newly created calendar entry ID
- `ref`: Auto-generated reference string (format: `group-{group_id}{session_id}{local_id}{account_id}-{random_3_digits}`)
- `color`: Randomly generated hex color for calendar display (ensured unique)
- `status`: Always set to 1 (active)
- `enabled`: Always set to 1 (enabled)
- `teacher_present`: Initialized to 0
- `force_teacher_present`: Initialized to 0
- `slc_use`: Always set to 1

**Auto-Generated Fields:**
- `color`: Random hex color (#000000 - #FFFFFF), guaranteed unique
- `ref`: Unique reference identifier
- `created_at`: Current timestamp
- `timestamp`: Current timestamp
- `refresh`: Set to 0
- `updated_at`: Set to NULL initially

**Validation Logic:**

**Time Overlap Detection:**
The system checks if a new session overlaps with existing sessions by verifying:
- Same date (based on `start_time`)
- New session starts before existing session ends (`start_time < existing.end_time`)
- New session ends after existing session starts (`end_time > existing.start_time`)

**Color Uniqueness:**
- Generates random hex color
- Checks if color is already in use
- Retries up to 50 times
- Fails if no unique color found after 50 attempts

**Notes:**
- All datetime fields must use format: `YYYY-MM-DD HH:MM:SS`
- Conflict checks only apply to **enabled** calendar entries (`enabled = 1`)
- Conflicts are checked for the **same day only** (not across different days)
- Empty strings and null values are both rejected during validation
- The endpoint returns HTTP 402 for conflicts (not 409) to distinguish from validation errors

**Example Use Cases:**

**Scenario 1: Create Morning Lecture**
```json
{
  "session_id": 2,
  "account_id": 1,
  "local_id": 1,
  "group_id": 3,
  "room_id": 5,
  "teacher_id": 12,
  "subject_id": 8,
  "description": "Introduction to calculus fundamentals",
  "start_time": "2026-01-30 08:00:00",
  "end_time": "2026-01-30 10:00:00",
  "title": "Calculus 101",
  "type": "lecture"
}
```

**Scenario 2: Create Afternoon Lab**
```json
{
  "session_id": 3,
  "account_id": 2,
  "local_id": 2,
  "group_id": 8,
  "room_id": 2,
  "teacher_id": 15,
  "subject_id": 4,
  "description": "Hands-on chemistry experiments",
  "start_time": "2026-01-29 14:00:00",
  "end_time": "2026-01-29 16:30:00",
  "title": "Chemistry Lab Session",
  "type": "lab"
}
```

**Testing Conflicts:**

To test conflict detection, create overlapping sessions:

1. **Room Conflict Test:**
   - Create session with Room 5, 09:00-11:00
   - Try creating another with Room 5, 10:00-12:00
   - Expected: Room conflict error

2. **Group Conflict Test:**
   - Create session with Group 3, 09:00-11:00
   - Try creating another with Group 3, 10:30-12:30
   - Expected: Group conflict error

3. **Teacher Conflict Test:**
   - Create session with Teacher 10, 14:00-16:00
   - Try creating another with Teacher 10, 15:00-17:00
   - Expected: Teacher conflict error

---