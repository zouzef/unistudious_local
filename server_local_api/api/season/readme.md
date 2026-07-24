# Season Blueprint (`season_bp`)

Flask blueprint for `unistudious_local`, mounted at `/scl`. Currently a single endpoint for creating **seasons** (a time-boxed grouping under a `formation`, e.g. a term or cohort).

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| POST | `/scl/create-season` | Create a season under a formation |

## What it does

Inserts a row into `season` with `formation_id`, `account_id`, `title`, `description`, `type_duration`, `number_duration`, hardcoding `status = 1` and `enabled = 1`. On success, re-fetches the inserted row and attempts to write an audit log entry.

## 🔴 This endpoint will crash on every request — three blocking bugs

### 1. `log_audit` is used but never imported
The file has no `from util.audit import log_audit` (every other blueprint in the project does). The moment `create_season` reaches the success branch, this raises `NameError: name 'log_audit' is not defined`.

```python
from util.audit import log_audit
```

### 2. `log_audit()` call is missing the required `table_name` argument
Every other blueprint's call includes `table_name="<table>_audit"` as the first argument. Here it's omitted entirely:

```python
log_audit(
   action_type="INSERT",
   old_data=None,
   new_data=new_record[0] if new_record else data
)
```

Following the pattern used elsewhere (e.g. `formation_audit`, `camera_audit`), this should be:

```python
log_audit(
   table_name="season_audit",
   action_type="INSERT",
   old_data=None,
   new_data=new_record[0] if new_record else data
)
```
(Confirm the actual audit table name matches whatever exists in the schema — likely `season_audit`.)

### 3. `except Excepton as e:` — typo'd exception class
`Excepton` isn't a real name (should be `Exception`). Since bug #1 will already raise a `NameError` inside the `try` block, Python then tries to match it against `Excepton` in the `except` clause — but `Excepton` itself doesn't exist, so this raises a **second** `NameError` while handling the first. The result: instead of your intended `500` JSON error response, the client gets an unhandled server error (Flask's raw 500 traceback) with no useful message.

```python
except Exception as e:
```

## Other gaps worth addressing while you're in this file

- **No required-field validation.** Unlike other create endpoints in the project (`create_formation`, `create_group`, `create_camera`, etc.), there's no check that `formation_id`, `account_id`, `title`, etc. are present before attempting the insert — a missing field will just insert `NULL`s or fail at the DB layer with a less-clear error.
- **No `@token_required`** (import is present but unused) — consistent with other endpoints in the codebase that also leave auth commented out, so may be intentional for now, but worth a quick check.
- Once fixed, this endpoint would benefit from the same `if not data:` guard used elsewhere (`update_group`, `disaffect_user_group`) in case `request.get_json()` returns `None`.

## TODO

- Add the missing `import`, fix the `log_audit()` call signature, and fix the `Excepton` → `Exception` typo — all three are one-line changes but currently make this endpoint completely non-functional.
- Add required-field validation mirroring `create_formation`'s pattern.
- Consider adding `GET`/update/delete endpoints for seasons if this blueprint is meant to mirror the CRUD pattern used for formations and groups elsewhere in the project.