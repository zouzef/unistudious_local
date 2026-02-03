# Users API

Base URL: `/scl`

Authentication required for all endpoints.

Manages users, groups, teachers, and their relationships within sessions.

---

## Endpoints

### 1. Get Groups with Students
**GET** `/scl/get-group/<account_id>/<session_id>`

Get all groups for a session with their enrolled students.

**Parameters:**
- `account_id` (int): Account ID
- `session_id` (int): Session ID

**Response (200):**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": 1,
      "session_id": 5,
      "local_id": 3,
      "name": "Group A",
      "capacity": 30,
      "status": "Active",
      "list_student": [
        {
          "user_id": 123,
          "username": "john.doe",
          "full_name": "John Doe",
          "email": "john@example.com",
          "phone": "+216 12345678",
          "relation_id": 456
        },
        {
          "user_id": 124,
          "username": "jane.smith",
          "full_name": "Jane Smith",
          "email": "jane@example.com",
          "phone": "+216 87654321",
          "relation_id": 457
        }
      ]
    },
    {
      "id": 2,
      "session_id": 5,
      "local_id": 3,
      "name": "Group B",
      "capacity": 25,
      "status": "Active",
      "list_student": []
    }
  ]
}
```

**Field Descriptions:**

**Group Fields:**
- `id`: Group ID
- `session_id`: Associated session ID
- `local_id`: Associated local/building ID
- `name`: Group name
- `capacity`: Maximum group capacity
- `status`: Group status
- `list_student`: Array of students in this group

**Student Fields:**
- `user_id`: Student user ID
- `username`: Username
- `full_name`: Full name
- `email`: Email address
- `phone`: Phone number
- `relation_id`: Relation ID (from `relation_user_session`)

**Notes:**
- Excludes **special groups** (`special_group IS NULL`)
- Only returns **enabled groups and users** (`enabled = 1`)
- Groups without students return empty `list_student` array
- Results ordered by group ID, then username

**Response (500):**
```json
{
  "success": false,
  "message": "Error description",
  "data": [],
  "count": 0
}
```

---

### 2. Get Teachers by Session
**GET** `/scl/get_teacher/<session_id>`

Get all teachers assigned to a specific session.

**Parameters:**
- `session_id` (int): Session ID

**Response (200):**
```json
{
  "message": "success",
  "data": [
    {
      "id": 10,
      "username": "dr.smith",
      "full_name": "Dr. John Smith",
      "email": "smith@university.edu",
      "phone": "+216 11223344",
      "roles": "{\"0\":\"ROLE_TEACHER\",\"1\":\"ROLE_USER\"}",
      "enabled": 1,
      "created_at": "2026-01-01T10:00:00",
      "uuid": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

**Field Descriptions:**
- `id`: Teacher user ID
- `username`: Username
- `full_name`: Full name
- `email`: Email address
- `phone`: Phone number
- `roles`: JSON string of user roles (must contain `ROLE_TEACHER`)
- `enabled`: User is active (1) or disabled (0)
- `created_at`: Account creation timestamp
- `uuid`: Unique identifier

**Notes:**
- Only returns users with `ROLE_TEACHER` role
- Filters by users assigned to the session via `relation_user_session`
- Only includes **enabled users** (`enabled = 1`)

**Response (200) - No Teachers:**
```json
{
  "message": "success",
  "data": []
}
```

**Response (500):**
```json
{
  "message": "Error description"
}
```

---

### 3. Affect User to Group
**POST** `/scl/affect_user_group/<session_id>`

Assign a user to a group within a session.

**Parameters:**
- `session_id` (int): Session ID

**Request Body:**
```json
{
  "user_id": 123,
  "group_id": 5
}
```

**Process:**
1. Validates user exists and is enabled
2. Validates group exists and is enabled
3. Updates `relation_user_session` to assign user to group
4. Only affects users **not yet assigned** to any group

**Response (200):**
```json
{
  "status": "success",
  "message": "User assigned to group successfully",
  "data": {
    "user_id": 123,
    "group_id": 5,
    "session_id": 10
  }
}
```

**Response (400) - Missing Parameters:**
```json
{
  "status": "error",
  "message": "Missing user_id or group_id"
}
```

**Response (404) - User Not Found:**
```json
{
  "status": "error",
  "message": "User not found"
}
```

**Response (404) - Group Not Found:**
```json
{
  "status": "error",
  "message": "Group not found"
}
```

**Response (500):**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Notes:**
- Only updates users where `relation_group_local_session_id IS NULL`
- Updates only **one record** (LIMIT 1)
- User must be enabled
- Group must be enabled

---

### 4. Get Users Not Affected to Groups
**GET** `/scl/user_not_affected/<session_id>/<account_id>`

Get all users enrolled in a session but not assigned to any group.

**Parameters:**
- `session_id` (int): Session ID
- `account_id` (int): Account ID

**Response (200):**
```json
{
  "students": [
    {
      "userId": 123,
      "userName": "John Doe",
      "sessionId": 5,
      "sessionName": "Mathematics 101",
      "sessionCount": 1
    },
    {
      "userId": 124,
      "userName": "Jane Smith",
      "sessionId": 5,
      "sessionName": "Mathematics 101",
      "sessionCount": 2
    }
  ]
}
```

**Field Descriptions:**
- `userId`: Student user ID
- `userName`: Student full name (or username if full name unavailable)
- `sessionId`: Session ID
- `sessionName`: Session name
- `sessionCount`: Number of relations this user has in the session without group assignment

**Notes:**
- Only returns users where `relation_group_local_session_id IS NULL` or `= 0`
- Validates session belongs to the specified account
- Groups multiple relations by user ID
- Only includes **enabled users and relations** (`enabled = 1`)

**Response (404) - Session Not Found:**
```json
{
  "status": "error",
  "message": "Session not found."
}
```

**Response (500):**
```json
{
  "status": "error",
  "message": "Unexpected error occurred."
}
```

---

## Data Relationships
```
Account
  └── Session
       ├── Groups (relation_group_local_session)
       │    └── Users (via relation_user_session)
       └── Teachers (Users with ROLE_TEACHER)
```

**Key Tables:**
- `user` - User accounts
- `session` - Academic sessions
- `relation_group_local_session` - Groups within sessions
- `relation_user_session` - User-to-session-to-group relationships

---

## Use Cases

1. **Get groups with students** - View group organization and enrollment
2. **Get teachers** - List all teachers for a session
3. **Affect user to group** - Assign unassigned students to groups
4. **Get unaffected users** - Find students who need group assignment

---

## Error Responses

All endpoints may return:

**Response (500):**
```json
{
  "success": false,
  "message": "Error description"
}
```
or
```json
{
  "status": "error",
  "message": "Error description"
}
```

---

### 5. Delete Group
**POST** `/scl/delete-group/<group_id>`

Soft delete a group by disabling it and removing all user associations.

**Parameters:**
- `group_id` (int): Group ID to delete

**Process:**
1. Sets `enabled = 0` for the group (soft delete)
2. Removes group assignment from all users (sets `relation_group_local_session_id = NULL`)

**Response (200):**
```json
{
  "Message": "Group deleted successfully"
}
```

**Response (404) - Group Not Found:**
```json
{
  "Message": "Group not found"
}
```

**Response (500):**
```json
{
  "Message": "Error: error description"
}
```

**Notes:**
- This is a **soft delete** - group is disabled, not permanently removed
- All users previously assigned to this group will have their `relation_group_local_session_id` set to `NULL`
- Users remain enrolled in the session but become unassigned (can be reassigned to other groups)

---

### 6. Create Group
**POST** `/scl/create-group/<session_id>`

Create a new group within a session and assign a teacher-subject relationship.

**Parameters:**
- `session_id` (int): Session ID

**Request Body:**
```json
{
  "group_name": "Mathematics Group A",
  "capacity": 30,
  "subject_id": 5,
  "teacher_id": 10,
  "account_id": 1,
  "local_id": 2,
  "access_type": 0,
  "special_group": null
}
```

**Required Fields:**
- `group_name` (string): Name of the group
- `capacity` (int): Maximum number of students
- `subject_id` (int): Subject ID
- `teacher_id` (int): Teacher user ID
- `account_id` (int): Account ID
- `local_id` (int): Local/building ID

**Optional Fields:**
- `access_type` (int): Access type (default: 0)
- `special_group` (string/null): Special group designation (default: null)

**Process:**
1. Validates all required fields are present and non-empty
2. Creates group in `relation_group_local_session` table
3. Creates teacher-subject relationship in `relation_teacher_to_subject_group` table
4. Returns the newly created group ID

**Response (201):**
```json
{
  "Message": "Group created successfully",
  "group_id": 123
}
```

**Response (400) - Missing Fields:**
```json
{
  "Message": "Missing required fields"
}
```

**Response (500):**
```json
{
  "Message": "Error: error description"
}
```

**Field Descriptions:**
- `group_name`: Display name for the group
- `capacity`: Maximum enrollment limit
- `subject_id`: Links group to a subject
- `teacher_id`: Primary teacher assigned to this group
- `account_id`: Parent account
- `local_id`: Physical location/building
- `access_type`: Access level or type (0 = standard)
- `special_group`: Designation for special groups (e.g., "honors", "remedial")

**Notes:**
- Group is created with `status = 1` and `enabled = 1`
- Automatically creates timestamp fields (`created_at`, `timestamp`)
- Creates bidirectional relationship: group → teacher-subject
- `slc_use` is set to `1` by default for both records
- The teacher-subject relationship enables tracking which teacher teaches which subject for this group

**Example Use Case:**
```
1. Create group "Advanced Calculus" with capacity 25
2. Assign to Math subject (subject_id: 3)
3. Assign Dr. Smith as teacher (teacher_id: 15)
4. Group is now ready to receive student assignments
```

---