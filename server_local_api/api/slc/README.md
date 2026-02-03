# SLC (Physical Infrastructure) API

Base URL: `/scl`

Authentication required for all endpoints.

Manages physical infrastructure including rooms, locals (buildings/locations), and their configurations.

**SLC** = Smart Learning Center (physical infrastructure management)

---

## Endpoints

### 1. Get All Rooms
**GET** `/scl/get-all-room`

Get a list of all rooms in the system.

**Response (200):**
```json