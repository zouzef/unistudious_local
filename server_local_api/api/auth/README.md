# Authentication API

Base URL: `/scl`

## Endpoints

### 1. User Login
**POST** `/scl/login`

Authenticate a user and get a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

---

### 2. Device (SLC) Login
**POST** `/scl/login_slc`

Authenticate a device using MAC address and get a JWT token.

**Request Body:**
```json
{
  "mac": "AA:BB:CC:DD:EE:FF",
  "password": "string"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (401):**
```json
{
  "error": "Invalid credentials"
}
```