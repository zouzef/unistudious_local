# Devices Blueprint (`devices_bp`)

Flask blueprint for `unistudious_local`, mounted at `/scl`. Manages three device types tied to physical rooms: **cameras**, **tablets**, and **SLC doors** (smart lock controllers). Every create/update/delete operation writes to its own `*_audit` table via `log_audit()`, which the sync pusher later picks up to push changes to the remote server.

## Endpoints

### Cameras
| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get-all-camera` | List all enabled cameras, joined with room name |
| GET | `/scl/get-all-camera-room/<room_id>` | List cameras for one room |
| GET | `/scl/view-camera/<camera_id>` | Get a single camera + room name |
| POST | `/scl/create_camera` | Create a camera (username/password required only for `type == "ipcam"`) |
| POST | `/scl/delete_camera/<camera_id>` | Soft-delete (`enabled = 0`) |
| POST | `/scl/update_camera/<camera_id>` | Partial update — only `type`, `name`, `mac_id` are updatable |

### Tablets
| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get-all-tablets` | List all enabled tablets |
| GET | `/scl/get-all-tablet-room/<room_id>` | List tablets for one room |
| GET | `/scl/view-tablet/<id_tablette>` | Get a single tablet + room + owning SLC's username |
| POST | `/scl/create_tablet` | Create a tablet |
| POST | `/scl/delete_tablet/<tablet_id>` | Soft-delete |
| POST | `/scl/update_tablet/<tablet_id>` | Partial update — `name`, `mac_id`, `password` |

### SLC Doors
| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get_all_door` | List all enabled doors, joined through `slc_local` → `local` for building name |
| GET | `/scl/view_detail_door/<door_id>` | Get a single door + room name |
| POST | `/scl/create_door/<account_id>` | Create a door — **see known issue below** |
| POST | `/scl/delete_door/<door_id>` | Soft-delete |
| POST | `/scl/update_door/<door_id>` | Partial update — `name`, `status`, `mac_id`, `password`, `room_id` |
| POST | `/scl/change_staus_door/<mac_id>` | Set open/closed state (`oc` column) by MAC address, no audit log |
| GET | `/scl/check_slc_open` | Test/health-check endpoint — marked for removal in code comments |

## Conventions used throughout

- **Soft delete only** — every delete sets `enabled = 0`, never removes rows.
- **Audit trail** — create/update/delete on camera, tablet, and door all call `log_audit(table_name, action_type, old_data, new_data)` with `action_type` in `{"INSERT", "UPDATE", "DELETE"}`, matching what the sync pusher expects for these tables.
- **Dynamic partial updates** — update endpoints build `SET` clauses only for fields present in the request body, via an `allowed_fields` allow-list.
- **`Database.execute_query(query, values, fetch=False)`** returns a truthy insert/update result used to gate whether the audit log fires.
- Most GET endpoints have `@token_required` commented out — currently unauthenticated.

## Known issues (found during review)

1. **`create_door` will crash on every call.** The route declares `<int:account_id>` but the function signature `def create_door():` doesn't accept it — Flask raises a `TypeError` immediately. Needs `def create_door(account_id):` (and to actually use it), or the URL param should be dropped if it's not needed.

2. **`get_all_cameras_by_room` always returns `roomName: null`.** Its query (`SELECT * FROM camera WHERE room_id = %s...`) never joins `room`, but the code reads `row.get("room_name")` as if it did. Needs the same `c.*, r.name as roomName` join pattern used in `get_all_cameras`.

3. **`delete_camera`'s exception handler returns no status code**, defaulting to `200` on failure — inconsistent with every other endpoint's `500` on error.

4. **`change_staus_door` doesn't call `log_audit()`** — status changes on doors aren't tracked in `slc_door_audit`, unlike every other door mutation. Worth confirming if that's intentional (e.g. too high-frequency to audit) or an oversight.

5. **`check_slc_open`** is explicitly commented as a test endpoint to delete after testing — still present.

## TODO / cleanup candidates

- Decide whether `account_id` in `create_door`'s route should be stored on the door record (e.g. for multi-tenant scoping like other resources) or removed entirely.
- Re-enable `@token_required` on GET endpoints once auth is ready, or confirm they're intentionally public on the local network.
- Add `log_audit` to `change_staus_door` if door open/close events should be tracked remotely.