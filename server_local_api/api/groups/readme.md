# Group Blueprint (`Group_bp`)

Flask blueprint for `unistudious_local`, mounted at `/scl`. Manages **groups** (`relation_group_local_session`) within a session: creating/updating/deleting groups, assigning teachers/subjects to a group, and affecting/disaffecting students to/from a group. Backs the frontend `group_config.js` drag-and-drop group management UI.

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get-group/<account_id>/<session_id>` | Get all groups for a session, each with its student list and teacher/subject relations |
| POST | `/scl/affect_user_group/<session_id>` | Assign a student to a group |
| POST | `/scl/disaffect_user_group/<session_id>` | Remove a student from a group |
| GET | `/scl/user_not_affected/<session_id>/<account_id>` | List students in the session not yet assigned to any group |
| POST | `/scl/delete-group/<group_id>` | Soft-delete a group and clear its members' group assignment |
| POST | `/scl/create_group/<session_id>` | Create a group with its teacher/subject relations |
| POST | `/scl/update_group/<group_id>` | Update a group's name/capacity, and diff+replace its teacher/subject relations |

## Data model touched

- `relation_group_local_session` — the group itself (`name`, `capacity`, `status`, `special_group`, `access_type`, `slc_use`)
- `relation_user_session` — links a student (`user_id`) to a session and, once affected, to a group via `relation_group_local_session_id`
- `relation_teacher_to_subject_group` — links a group to one or more `(subject_id, teacher_id)` pairs
- `relation_group_local_session_audit` — audit trail for all group mutations, consumed by the sync pusher's `group_pusher`

## Endpoint details

### `get_group`
Two-query approach: one query pulls groups + their students (`LEFT JOIN relation_user_session` → `LEFT JOIN user`), a second pulls teacher/subject relations (`INNER JOIN` back to the same group scope). Both result sets are then merged in Python, keyed by `group_id`. The subject name resolution branches on whether `rtsg.subject_id = 1` (→ `account_subject.other_subject`) or not (→ `subject_config.name`) — `subject_id = 1` is being used as a sentinel for "custom/other subject," so it's a magic number worth a named constant if it isn't one already.

### `affect_user_group_endpoint` / `disaffect_user_group`
Both find the specific `relation_user_session` row for the given user/session (affect: `relation_group_local_session_id IS NULL`; disaffect: matches the current `group_id`), then flip that FK to the group ID or `NULL`, and log the change.

### `delete_group`
Soft-deletes the group (`enabled = 0`) and clears `relation_group_local_session_id` back to `NULL` for every member, so students become "unaffected" rather than orphaned.

### `create_group`
Inserts the group row, then loops `relations` to insert one `relation_teacher_to_subject_group` row per `(subject_id, teacher_id)` pair.

### `update_group`
The most complex endpoint: updates name/capacity, then **diffs** incoming `relations` against the existing ones (matched by `relation_id`) to classify each as added / updated / deleted, before disabling all old relation rows and re-inserting the full new set. The diff itself is only used to build a richer audit payload — the actual DB replace is unconditional (disable-all-then-reinsert-all), not selective per the diff.

## ⚠️ Known issue: `AFFECT` / `DISAFFECT` audit action types are silently dropped

```python
log_audit(
    table_name="relation_group_local_session_audit",
    action_type="AFFECT",   # or "DISAFFECT"
    ...
)
```

The sync pusher's handler map for `relation_group_local_session_audit` only recognizes `"INSERT"`, `"UPDATE"`, `"DELETE"`. Since `"AFFECT"`/`"DISAFFECT"` aren't registered keys, `_process_audit_rows` logs an "Unknown action" warning and skips the row — **it never gets pushed to remote and never gets marked as synced.** Every affect/disaffect currently silently fails to sync.

**Fix:** call `log_audit(..., action_type="UPDATE", ...)` instead, and put the semantic meaning ("affected"/"disaffected") inside `old_data`/`new_data` — which both endpoints already do via the `"group_id"` field flipping between `None` and a real ID (and `disaffect_user_group` already tags `"operation": "disaffect_user_from_group"` in its payload). Only the `action_type` string needs to change; the payload shape doesn't need rework.

## Other observations

- **`update_group`'s audit payload uses dynamic dict keys** like `f"deleteRelationIds[{delete_idx}]"` where `delete_idx` is a comma-joined string of indices (e.g. `"0,1,2"`). This produces keys such as `"deleteRelationIds[0,1,2]"` — unusual and likely awkward for anything downstream that expects consistent, parseable keys (including whatever eventually consumes this audit row on the remote side). A plain list under a fixed key (e.g. `"deleteRelationIds": [...]`) would be simpler to consume.
- **`create_group` and `delete_group`/`update_group` parse `Database.execute_query`'s return value differently** — `create_group` checks `isinstance(result, int)`, then two different dict shapes (`'lastrowid'`, `'id'`); `delete_group`/`update_group` check `result == 0` or a dict `'rowcount'`. Worth confirming what `Database.execute_query(..., fetch=False)` actually returns and standardizing on one check across the file (and ideally the codebase).
- **Duplicate "ENDPOINT 6" comment blocks** above `update_group` — four repeated headers, likely leftover from copy/paste edits. Harmless but worth trimming.
- **`get_group` has no session/account existence check** before running its main query (unlike `user_not_affected`, which validates the session first) — an invalid `session_id`/`account_id` just returns an empty group list rather than a 404, which may or may not be the desired behavior for the frontend.

## TODO / cleanup candidates

- Apply the `action_type="UPDATE"` fix to `affect_user_group_endpoint` and `disaffect_user_group` — this is the top-priority fix since it's actively causing data loss on sync.
- Simplify the `update_group` audit payload's dynamic-key structure to plain lists.
- Standardize the insert/update "did it succeed" return-value check across endpoints.
- Remove the duplicated comment headers above `update_group`.