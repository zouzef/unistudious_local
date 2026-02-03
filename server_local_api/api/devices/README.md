# Devices API

Base URL: `/scl`

Authentication required for all endpoints.

Manages cameras and tablets used for attendance tracking.

---

## Camera Endpoints

### 1. Get All Cameras
**GET** `/scl/get-all-camera`

Get a list of all cameras in the system.

**Response (200):**
```json
[
  {
    "id": 1,
    "type": "IP Camera",
    "name": "Camera Room 101",
    "mac": "AA:BB:CC:DD:EE:FF",
    "username": "admin",
    "password": "pass123",
    "status": "Active",
    "roomId": 5,
    "roomName": "Room 101",
    "created_at": "2026-01-15 10:30:00"
  }
]
```

---

### 2. Get All Cameras by Room
**GET** `/scl/get-all-camera-room/<room_id>`

Get all cameras assigned to a specific room.

**Parameters:**
- `room_id` (int): Room ID

**Response (200):**
```json
[
  {
    "id": 1,
    "type": "IP Camera",
    "name": "Camera Room 101",
    "mac": "AA:BB:CC:DD:EE:FF",
    "username": "admin",
    "password": "pass123",
    "status": "Active",
    "roomId": 5,
    "roomName": "Room 101",
    "created_at": "2026-01-15 10:30:00"
  }
]
```

---

### 3. Get Camera by ID
**GET** `/scl/view-camera/<camera_id>`

Get detailed information about a specific camera.

**Parameters:**
- `camera_id` (int): Camera ID

**Response (200):**
```json
{
  "success": true,
  "camera": {
    "id": 1,
    "type": "IP Camera",
    "name": "Camera Room 101",
    "mac_id": "AA:BB:CC:DD:EE:FF",
    "username": "admin",
    "password": "pass123",
    "status": "Active",
    "roomId": 5,
    "roomName": "Room 101",
    "created_at": "2026-01-15T10:30:00"
  }
}
```

**Response (404):**
```json
{
  "success": false,
  "message": "Camera not found"
}
```

---

## Tablet Endpoints

### 4. Get All Tablets
**GET** `/scl/get-all-tablets`

Get a list of all tablets in the system.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Tablet 1",
    "mac": "11:22:33:44:55:66",
    "password": "tablet123",
    "status": "Active",
    "roomId": 5,
    "roomName": "Room 5"
  },
  {
    "id": 2,
    "name": "Tablet 2",
    "mac": "AA:BB:CC:DD:EE:FF",
    "password": "tablet456",
    "status": "Inactive",
    "roomId": null,
    "roomName": "No Room Assigned"
  }
]
```

---

### 5. Get All Tablets by Room
**GET** `/scl/get-all-tablet-room/<room_id>`

Get all tablets assigned to a specific room.

**Parameters:**
- `room_id` (int): Room ID

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Tablet 1",
    "mac": "11:22:33:44:55:66",
    "password": "tablet123",
    "status": "Active",
    "roomId": 5,
    "roomName": "Room 5"
  }
]
```

---

### 6. Get Tablet by ID
**GET** `/scl/view-tablet/<id_tablette>`

Get detailed information about a specific tablet.

**Parameters:**
- `id_tablette` (int): Tablet ID

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Tablet 1",
    "mac": "11:22:33:44:55:66",
    "password": "tablet123",
    "status": "Active",
    "roomId": 5
  }
]
```

**Response (404):**
```json
{
  "status": "error",
  "message": "Tablet not found"
}
```

---

## Error Responses

All endpoints may return:

**Response (500):**
```json
{
  "message": "Internal Server Error"
}
```
or
```json
{
  "status": "error",
  "message": "Error description"
}
```