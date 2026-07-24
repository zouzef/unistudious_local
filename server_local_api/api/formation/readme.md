# Formation Blueprint (`formation_bp`)

Flask blueprint for `unistudious_local`, mounted at `/scl`. Handles CRUD for **formations** (course/program definitions) scoped to an `account_id`. Create/update/delete all write to `formation_audit` via `log_audit()` for the sync pusher to push to remote.

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get-formation-info/<account_id>` | List all enabled formations for an account (summary fields) |
| GET | `/scl/view_formation/<formation_id>` | Get full detail of one formation |
| POST | `/scl/create_formation/<account_id>` | Create a formation |
| POST | `/scl/update_formation/<formation_id>` | Partial update via `field_map` (camelCase → snake_case) |
| POST | `/scl/delete_formation/<formation_id>/<account_id>` | Soft-delete (`enabled = 0`), scoped to account |

## Conventions used

- **Soft delete** — `delete_formation` sets `enabled = 0` + `updated_at = NOW()`, never removes the row. Delete is scoped by both `formation_id` AND `account_id`, so it silently no-ops if the two don't match (see known issue #2).
- **`check_formation(formation_id)`** — shared helper checking `enabled = 1` existence; returns `False` on any DB error rather than raising, so callers can't distinguish "not found" from "DB error."
- **`field_map` + `nullable_fields` pattern** (in `update_formation`) — the standard approach used elsewhere in the codebase for partial updates from camelCase JS payloads: only keys present in `field_map` are updatable, and keys in `nullable_fields` get empty string coerced to `None` before hitting the DB.
- **Audit log** — `log_audit(table_name="formation_audit", action_type=..., old_data=..., new_data=...)` with `action_type` in `{"INSERT", "UPDATE", "DELETE"}`, matching what the sync pusher's `formation_audit` handler expects.

## Known issues (found during review)

1. **`create_formation` uses `LAST_INSERT_ID()` instead of `cursor.lastrowid`.** This is the same pattern that was already identified as unreliable with connection pools elsewhere in the project (see the shared `util/audit.py` fix) — under a pooled connection, a second query on the same call can land on a different pooled connection, making `LAST_INSERT_ID()` return the wrong ID or `NULL`. Should use `Database.execute_query(..., fetch=False)`'s return value (the inserted ID) directly, the way other creation endpoints in the project do, rather than a follow-up `SELECT ... WHERE id = LAST_INSERT_ID()`.

2. **`delete_formation` can silently no-op.** The `UPDATE ... WHERE id = %s AND account_id = %s` won't match (and `result` will be falsy) if `formation_id` exists but belongs to a different `account_id`. `check_formation()` only checks `id`, not `account_id`, so the 404 branch won't catch this case — it'll instead fall through to `"Message": "Failed to delete formation"` with a 400, which is a bit misleading (looks like a general failure rather than an ownership mismatch).

3. **`view_formation`'s exception handler returns no HTTP status code**, so Flask defaults to `200` even on error — inconsistent with every other endpoint in this file, which return `500`.

4. **Tab/space mixing** — this file uses tabs in some functions (`get_formation_info`, `check_formation`, `view_formation`) and spaces in others (`update_formation`, `create_formation`, `delete_formation`). Not a functional bug in Python 3 as long as it's not mixed *within* a single block, but worth normalizing to avoid a future `TabError` if someone edits across the boundary.

## TODO / cleanup candidates

- Standardize on `cursor.lastrowid` (or whatever `Database.execute_query` already returns on insert) instead of `LAST_INSERT_ID()` across all creation endpoints, not just this file.
- Decide whether `delete_formation`'s account-mismatch case should return a distinct error (e.g. 403/404) instead of a generic "Failed to delete."
- Run the file through a formatter (e.g. `black`) to eliminate the tabs/spaces inconsistency.