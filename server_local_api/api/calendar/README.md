# DataPusher — Local-to-Remote Sync Module

Part of `unistudious_local`'s data synchronization system. `DataPusher` scans local **audit tables** for unsynced rows (`is_synced = 0`) and pushes each change to the remote production server (unistudious.com), marking rows as synced on success.

## How it works

1. `detect_and_push_local_changes(db)` is the entry point, called on a sync cycle.
2. For each domain (User, Virtual User, Group, ...), it queries the matching `*_audit` table for rows where `is_synced = 0`, ordered by `audit_id`.
3. Each batch of rows is handed to `_process_audit_rows()` along with an `action_handlers` dict mapping `action_type` → pusher function.
4. For every row:
   - The handler for `row['action_type']` is looked up.
   - If no handler matches, the row is **skipped and logged as a warning** — it stays `is_synced = 0` and will be retried (uselessly) every cycle unless someone notices the warning.
   - If a handler exists, it's called with `(db, settings, row)`.
   - On success (`True`), `is_synced` is set to `1` and committed.
   - On failure (`False`), the row is left for retry next cycle.

```
audit table (is_synced = 0)
        │
        ▼
_process_audit_rows()
        │
        ▼
action_handlers[row.action_type](row)
        │
   ┌────┴────┐
 success   failure
   │           │
mark synced   retry next cycle
```

## Active domains

| Table | Actions handled | Pusher module |
|---|---|---|
| `user_audit` | `CREATE`, `UPDATE`, `DELETE` | `user_pusher` |
| `virtual_user_audit` | `CREATE`, `UPDATE`, `DELETE` | `virtuel_pusher` |
| `relation_group_local_session_audit` | `INSERT`, `UPDATE`, `DELETE` | `group_pusher` |

## Disabled domains (commented out)

Calendar, attendance, account level/section/subject/tag, completion tag, association folders/images, and SLC devices (door, camera, tablet) are currently commented out of `detect_and_push_local_changes`. They still have handler logic written but are not being executed. Re-enabling any of them just means uncommenting the relevant block — the `_process_audit_rows` machinery already supports them.

## ⚠️ Known issue: `action_type` mismatches are silently dropped

`_process_audit_rows` only pushes a row if its `action_type` exists as a key in that table's `action_handlers` dict. If `log_audit()` is called elsewhere in the codebase with an `action_type` that isn't one of the registered keys (e.g. `"AFFECT"` / `"DISAFFECT"` instead of `"INSERT"` / `"UPDATE"` / `"DELETE"`), the row:

- **Is not pushed to remote**
- **Is not marked as synced**
- Only shows up as a `logger.warning("Unknown action: ...")` line, easy to miss in normal logs

**Fix:** use one of the action types already registered for that table (typically `"INSERT"`, `"UPDATE"`, `"DELETE"`, or `"CREATE"` depending on the domain), and encode the semantic meaning (e.g. "affected"/"disaffected") inside the audit **payload** rather than in `action_type`. `action_type` should stay limited to the small, fixed set of keys each `action_handlers` dict actually recognizes.

## Adding a new domain to sync

1. Ensure the domain has a `*_audit` table with at least `audit_id`, `action_type`, `is_synced`.
2. Write pusher functions (typically in `sync/pushers/<domain>_pusher.py`) that accept `(db, settings, row)` and return `True`/`False`.
3. In `detect_and_push_local_changes`, add a block:
   ```python
   cursor.execute("""
       SELECT * FROM <domain>_audit
       WHERE is_synced = 0
       ORDER BY audit_id ASC
   """)
   rows = cursor.fetchall()
   if rows:
       self._process_audit_rows(
           cursor, conn,
           "<domain>_audit",
           rows,
           {
               "INSERT": lambda row: <domain>_pusher.push_add(db, self.settings, row),
               "UPDATE": lambda row: <domain>_pusher.push_update(db, self.settings, row),
               "DELETE": lambda row: <domain>_pusher.push_delete(db, self.settings, row),
           }
       )
   ```
4. Make sure every `action_type` your app ever writes via `log_audit()` for this table has a matching key here — otherwise it silently falls into the "unknown action" trap above.

## Open TODO

- Consolidate pusher imports through a central `registry.py` instead of importing each pusher module individually at the top of this file.
- Consider having `_process_audit_rows` raise/log at a higher severity (or push a metric/alert) when it hits an unknown `action_type`, since a plain `logger.warning` is too easy to miss in production.