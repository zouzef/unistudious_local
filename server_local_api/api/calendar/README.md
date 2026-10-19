# Calendar API (`calendar_bp`)

Flask blueprint managing session calendars: creation (single and recurring), conflict checks, calendar requests (approve/reject), special groups, notifications, and door/room lookups.

- **Blueprint:** `calendar_bp`, `url_prefix='/scl'`
- **DB access:** `Database.execute_query(query, values, fetch=True|False)`
  - `fetch=True` (default) returns a list of dict rows
  - `fetch=False` returns the inserted id / truthy result
- **Auth:** `token_required` is imported but **commented out** on every route. All endpoints are currently public.
- **Soft deletes:** `enabled = 0` (never hard delete)

## Main tables

| Table | Purpose |
|---|---|
| `relation_calander_group_session` | Calendar entries (events) |
| `relation_calander_group_audit` | Audit log for calendar inserts (`is_synced` for sync) |
| `calendar_request` | Pending teacher/user requests (`accepted`: 0 pending, 1 approved, 2 rejected) |
| `relation_group_local_session` | Groups (`special_group` flag) |
| `relation_user_session` | Users enrolled in a group |
| `attendance` / `attendance_audit` | Attendance rows generated per calendar entry |
| `relation_completion_tag` | Tags linked to a calendar entry |
| `relation_teacher_to_subject_group` | Teacher/subject link for a group |
| `notification` | Stored notifications |
| `room`, `local`, `session`, `user`, `account`, `account_subject`, `subject_config`, `slc_door` | Reference data |

---

## Endpoints

### Calendar read

| # | Method | Route | Description |
|---|---|---|---|
| 2 | GET | `/scl/get_calander_id/<int:id_calender>` | Calendar row by id (`enabled=1`). 404 if missing. |
| 3 | GET | `/scl/get-group-calender/<int:calendarId>` | Returns `{group_session_id}` for a calendar. |
| 4 | GET | `/scl/get_next_session/<int:calendarId>` | Next calendar (by `start_time`) after the given one. Returns `{"data": null}` if none. Not filtered by group/room/enabled. |
| 5 | GET | `/scl/get-all-calender` | Today's remaining sessions (UTC date; includes entries ending within the last 5 min). Joins teacher, subject, local, room, session. |
| 6 | GET | `/scl/data_account/<int:id>` | Account row linked to a calendar id. |
| 7 | GET | `/scl/get_calendar_session/<int:id_session>/<int:id_account>` | Entries for a session+account. Datetimes shifted **+1h** (Tunisia) and returned as ISO strings. |
| 10 | GET | `/scl/get-calendar-room/<int:room_id>` | All enabled entries for a room (with teacher `username`). 404 if room unknown or no data. |
| 20 | GET | `/scl/get_TeacherId_calander/<int:calender_id>` | Teacher `{username, id}` for a calendar. |
| 21 | GET | `/scl/get_calander_now/<date>/<time>` | Entries active at a given `date` (`YYYY-MM-DD`) and `time` (`HH:MM:SS`). |
| 21 | GET | `/scl/get-calendar-door/<door_id>` | Ongoing/upcoming type `'P'` entries for the room linked to a door MAC. |
| – | GET | `/scl/get-calender-moderateur/<int:session_id>/<int:account_id>` | Today's entries for a session+account (moderator view). |
| – | GET | `/scl/get_all_calander/<int:account_id>` | All enabled entries for an account (with group, room, teacher names). |
| – | GET | `/scl/get-id-prod/<int:calendar_id>` | `{id_prod}` of a calendar (or `null`). |

### Calendar delete

**POST `/scl/deleting_interval/<int:session_id>`**

Body:
```json
{ "start_date": "YYYY-MM-DD HH:MM:SS", "end_date": "YYYY-MM-DD HH:MM:SS" }
```
Soft-deletes (`enabled=0`) every calendar overlapping the interval (`start_time <= end_date AND end_time >= start_date`).
Responses: `200 {"message":"success","data":[{id}...]}`, `400` (missing/invalid dates or no match).

### Create calendar (single or recurring)

**POST `/scl/create_calender`**

Required body fields: `session_id, account_id, local_id, group_id, room_id, teacher_id, subject_id, start_time, end_time, title, type`
Optional: `description`, `completionTags` (list of tag ids), `duplicate`, `endDate`

```json
{
  "session_id": 1, "account_id": 2, "local_id": 3, "group_id": 4,
  "room_id": 5, "teacher_id": 6, "subject_id": 7,
  "start_time": "2026-10-20 09:00:00", "end_time": "2026-10-20 10:30:00",
  "title": "ignored", "type": "P",
  "description": "", "completionTags": [1, 2],
  "duplicate": "weekly", "endDate": "2026-12-20"
}
```

- `title` must be present but is **overridden** by the group's name (`get_name_group`), falling back to `"Unknown Group"`.
- `duplicate`: `none` (default) | `daily` (+1d) | `weekly` (+7d) | `biweekly` (+14d). Requires `endDate` (`YYYY-MM-DD`, inclusive, not before the start date).
- `start_time` / `end_time` accept `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD HH:MM`. Each occurrence keeps the same time of day.

**Per occurrence** (`_create_single_calendar_row`):
1. Conflict checks: room, group, teacher (overlap on same date)
2. Unique random hex color (50 attempts max)
3. Insert into `relation_calander_group_session` (+ unique `ref` like `group-<ids>-<3 digits>`)
4. Insert audit row (`INSERT`, `is_synced=0`)
5. Insert completion tags
6. Insert one `attendance` row per user in the group (`is_present=0`, `is_editable=1`) + `attendance_audit` row

**Responses**
- `200` `{"Message", "entries": [{calander_id, date, ref, color, attendance_created}], "attendance_created": N}`
- `400` missing/empty fields, bad/missing `endDate`
- `402` conflict: `Room-Conflict`, `Group-Conflict`, `Teacher-Conflict`, or color failure. Includes `occurrence_date` and `created_before_failure`.
- `500` internal error

> No rollback: if occurrence N conflicts, occurrences 1..N-1 stay created (returned in `created_before_failure`).

### Calendar requests

| Method | Route | Description |
|---|---|---|
| POST | `/scl/create-calander_request/<int:session_id>` | Create a request. Body: `room_id, group_id, subject_id, user_id, tag (list), duplicate, start_date, start_time, end_time, end_date, description, account_id, type`. Validates room/user/subject/group, inserts into `calendar_request`, saves a notification and POSTs to the Academie platform. |
| GET | `/scl/get-calander_request/<int:room_id>` | Pending (`accepted=0`, `enabled=1`) requests for a room. |
| GET | `/scl/get-calander_requestt/<int:account_id>` | All enabled requests for an account (note the double `t` in the route). |
| POST | `/scl/approve_calander_request/<int:request_id>` | Runs conflict checks (auto-rejects the request on conflict, returns 402), then creates a calendar entry and sets `accepted=1`. |
| POST | `/scl/reject_calander_request/<int:request_id>` | Sets `accepted=2`. |
| POST | `/scl/delete_calander_request/<int:request_id>` | Soft delete (`enabled=0`). |

Approve creates a **single** entry only (no recurrence, no attendance, no audit, no completion tags), unlike `/create_calender`.

### Notifications

**GET `/scl/get-notification/<account_id>`** returns
```json
{ "success": true, "notifications": [{id, user_id, title, message, type, is_read, created_at, data}], "total": 0, "unread_count": 0 }
```
Sorted unread first, then newest. `notif_data` is parsed from JSON.

`send_notification(payload)` (internal): stores the notification (`type='tablet_notif'`), then POSTs to `https://192.168.1.246:5015/api/notify-calendar-request` (`verify=False`, 5s timeout). Failures are logged and never raised.

### Special groups

**POST `/scl/create_calender_special_group`**

Required: `name, teacher_id, subject_id, capacity, session_id, access_type, type, room_id, start_date, start_time, end_time, description, is_special, completion_tags`, plus `end_date` (key must exist, may be null). Also reads `local_id` and `account_id` (not validated).

Flow: room + teacher conflict check → create group (`relation_group_local_session`) → create calendar entry → link teacher to subject (`relation_teacher_to_subject_group`) → audit insert.
Times are built as `"{start_date} {start_time}:00"`, so `start_time`/`end_time` must be `HH:MM`.

**POST `/scl/cronjob_calander_special/<int:calander_id>`**

If the calendar's group is special (`special_group=1`), sets `relation_group_local_session_id = NULL, slc_use = 1` for all `relation_user_session` rows of that group (detaches the users). Returns `200` "Group is not special" otherwise, `404` if the group has no users.

---

## Helper functions

| Function | Description |
|---|---|
| `generate_random_color()` | Random `#RRGGBB` |
| `check_color(color)` | True if the color is already used by an enabled entry |
| `generate_unique_ref(group, session, local, account)` | `group-<g><s><l><a>-<3 digits>` |
| `isRoomReserved / isGroupTypeConflit / isSubjectTeacherConflit` | Overlap check on same date: `TIME(start) < end AND TIME(end) > start` |
| `get_name_group(id)` | Group name or `None` |
| `create_completion_tag(data, calender_id)` | Inserts tags from `data['completionTags']` |
| `parse_flexible_datetime(str)` | Parses `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d %H:%M` |
| `_combine_date_time(base_str, new_date)` | Moves a datetime string onto another date, keeping the time |
| `_build_occurrence_dates(start_dt, type, end_date)` | List of recurrence dates |
| `_create_single_calendar_row(...)` | Full creation pipeline for one occurrence |
| `check_room_id / check_session / check_group / check_user / check_subject / check_calander_request_id / check_door_id` | Existence checks |
| `get_room_id(door_id)` | Room id for a door MAC |
| `save_notification / send_notification` | Persist and push notifications |
| `create_special_group / create_calander_special / create_relation_teacher_to_subject` | Special-group inserts |
| `test_special_group(calander_id)` | `(is_special, group_id)` |

---

## Known issues / things to fix

1. **No authentication**: `@token_required` is commented out on all routes. `deleting_interval` and the approve/reject routes are open.
2. **`deleting_interval` ignores `session_id`**: it soft-deletes every overlapping calendar across all sessions/accounts. Add `AND session_id = %s`.
3. **Conflict checks fail open**: `isRoomReserved`, `isGroupTypeConflit`, `isSubjectTeacherConflit` return `False` on DB error, so a DB failure lets a double-booking through. `check_color` returns `None` on empty result and `True` on error.
4. **Conflict checks compare `TIME()` on one `DATE(start_time)`**: they ignore entries that span midnight and don't check `session_id`/`account_id`.
5. **`get-calander_request/<room_id>` query**: `JOIN account_subject acs ON cr.subject_id = acs.id AND sc.name = 'other'` is an inner join, so rows whose subject isn't `'other'` are dropped. Also `'other'` (lowercase) vs `'Other'` in `get-all-calender`. Use `LEFT JOIN` and one consistent casing. Also joins on `acs.id = subject_id` where `get-calander_requestt` / `get-all-calender` use `subject_config_id`.
6. **`reject_calander_request`** returns status `5000` on error (should be `500`).
7. **`get_notification`** has a second unreachable `except` block after the first `try/except`.
8. **`send_notification`** URL has a leading space (`" https://..."`) and uses `verify=False`.
9. **`create_calander_special_group`**: `create_special_group` returns `False` (not a tuple) on failure, so `reponse, group_id = ...` raises. Group creation, calendar creation and teacher link are not transactional. `local_id`/`account_id` are not validated. `type` shadows the builtin.
10. **`approve_calander_request`**: joins `local l` on `account_id` only; if an account has several locals, multiple rows come back and the first is used arbitrarily. Missing attendance, audit and completion-tag creation compared to `/create_calender`.
11. **`/create_calender` recurrence** is not atomic (see above) and `get_name_group` queries `relation_group_local_session` by `group_id`, silently falling back to `"Unknown Group"`.
12. **Timezones are inconsistent**: `get-all-calender` uses `datetime.utcnow()`, `get_calendar_session` adds +1h manually, others return raw DB values.
13. **Cleanup**: unused imports (`FastParser` from `xmlrpc.client`, `jwt`, `log_audit`, `Config`, duplicate `datetime` import); `sys.path.append` runs after imports that may already need it; `traceback` imported inline in several places.
14. **Inconsistent response keys**: `Message`/`message`, `data`/`Data`, `error`/`Error`. Pick one convention.