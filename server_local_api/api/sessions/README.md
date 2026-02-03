# Sessions API

Base URL: `/scl`

Authentication required for all endpoints.

Manages academic sessions (courses/classes) with their configurations, pricing, and settings.

---

## Endpoints

### 1. Get Session Details by Account
**GET** `/scl/get_session_detail/<account_id>`

Get all sessions belonging to a specific account with full details.

**Parameters:**
- `account_id` (int): Account ID

**Response (200):**
```json