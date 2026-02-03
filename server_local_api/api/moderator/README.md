# Moderator API

Base URL: `/scl`

Manages moderator authentication and dashboard statistics.

---

## Endpoints

### 1. Authenticate Moderator
**POST** `/scl/authentification-moderateur`

Verify if a user has all required moderator roles.

**Required Moderator Roles:**
- `ROLE_MANAGER_ADMINISTRATIVE`
- `ROLE_MANAGER_CONFIG`
- `ROLE_MANAGER_FINANCE`
- `ROLE_MANAGER_HR`
- `ROLE_MANAGER_IT`
- `ROLE_MANAGER_MARKETING`
- `ROLE_CUSTOMER_MANAGER_SERVICE`

**Request Body (JSON):**
```json
{
  "username": "admin_user"
}
```

**Request Body (Form Data):**
```
username=admin_user
```

**Response (200) - Success:**
```json
{
  "message": "success"
}
```

**Response (400) - Missing Username:**
```json
{
  "message": "Username required"
}
```

**Response (404) - User Not Found:**
```json
{
  "message": "User Not Found"
}
```

**Response (403) - Insufficient Permissions:**
```json
{
  "message": "Insufficient permissions",
  "missing_roles": [
    "ROLE_MANAGER_FINANCE",
    "ROLE_MANAGER_IT"
  ]
}
```

**Response (500) - Invalid Roles Format:**
```json
{
  "error": "Invalid roles format"
}
```

---

### 2. Get Moderator Dashboard Statistics
**GET** `/scl/get_data_moderateur/<account_id>`

Get statistics for the moderator dashboard including counts of users, teachers, groups, and sessions.

**Parameters:**
- `account_id` (int): Account ID

**Authentication:** Required (token)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "nbuser": 150,
    "nbteach": 25,
    "nbgroup": 12,
    "nbsession": 8,
    "account_id": 1
  }
}
```

**Field Descriptions:**
- `nbuser`: Total number of users with `ROLE_USER` role
- `nbteach`: Total number of teachers with `ROLE_TEACHER` role
- `nbgroup`: Total number of active groups (`relation_group_local_session`)
- `nbsession`: Total number of active sessions
- `account_id`: The account ID requested

**Response (500) - Error:**
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Error description"
}
```

---

## Notes

- The authenticate endpoint does **NOT** require a token (it's used for initial authentication check)
- The dashboard statistics endpoint **requires authentication**
- User roles are stored as JSON in the database
- All counts only include enabled (`enabled = 1`) records