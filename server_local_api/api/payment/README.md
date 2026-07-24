# Payment Blueprint (`payment_bp`)

Flask blueprint for `unistudious_local`, mounted at `/scl`. Handles **payment sessions** (tuition/fee payments tied to a student + session) and **invoices**.

## Endpoints

### Payments
| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get_payment_session/<session_id>` | List payments for a session — **see known issue #1** |
| GET | `/scl/get_payment_session_user/<session_id>/<user_id>` | List payments for one student in a session |
| POST | `/scl/update_payment_session/<payment_id>` | Update a payment's `amount` only (legacy/simple form) |
| POST | `/scl/update_payment_session_user/<session_id>/<user_id>/<payment_id>` | Partial update of `amount`, `description`, `status` |

### Invoices
| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get_all_invoice/<account_id>` | List all enabled invoices for an account |
| GET | `/scl/get_invoice_by_id/<invoice_id>/<account_id>/<admin_user_id>` | Get one invoice with student/academy/admin/local details — **see known issue #2** |

## Conventions used

- Audit rows are written with a **raw `INSERT INTO payment_session_audit`** directly in each endpoint, rather than the shared `log_audit()` helper (`util/audit.py`) used by every other blueprint in the project. Old/new snapshots are JSON-serialized with `json.dumps(..., default=str)` before insert.
- `update_payment_session_user` builds its `SET` clause dynamically, only including fields present and non-`None` in the request body (`amount`, `description`, `status`), always appending `updated_at = NOW()`.

## ⚠️ Known issues (found during review)

### 1. `get_payment_session`'s `GROUP BY user_id` silently drops payments

```sql
SELECT p.id, ..., u.full_name, s.name
FROM payment_session p, user u, session s
WHERE session_id = %s AND p.enabled = 1 AND p.user_id = u.id AND s.id = p.session_id
GROUP BY user_id
ORDER BY created_at DESC
```

`GROUP BY user_id` collapses all rows to **one row per student**, but the `SELECT` list pulls non-aggregated columns (`p.id`, `p.amount`, `p.date_payment`, etc.) that aren't part of the grouping — under MySQL's default (non-`ONLY_FULL_GROUP_BY`) mode this doesn't error, it just picks an arbitrary row per group. In practice: if a student has multiple payments in a session, only one of them (indeterminate which) is returned, and the rest are silently invisible to this endpoint. If the intent was "all payments for this session," the `GROUP BY` should be removed entirely; if the intent was "one summary row per student," the query needs real aggregate functions (`SUM(p.amount)`, `MAX(p.date_payment)`, etc.) instead of raw columns.

### 2. `get_invoice_by_id` has a missing comma — this query will fail

```sql
a.name             AS academy_name,
a.file_link
-- Admin info (logged-in user)
admin.full_name     AS agent_name,
```

There's no comma after `a.file_link` before `admin.full_name`. SQL comments don't insert separators, so this is two adjacent column expressions with nothing between them — a syntax error. This endpoint will raise a DB exception on every call and always return the generic 500 handler. Needs:

```sql
a.name             AS academy_name,
a.file_link,
-- Admin info (logged-in user)
admin.full_name     AS agent_name,
```

Also worth double-checking column collisions once the syntax is fixed: `i.*` plus a later unaliased `l.name` means if `invoice` also has a `name` column, the result dict will have one silently overwrite the other (Python dict keys from `fetch=True` results are column names, and duplicates collapse to the last one returned).

### 3. Audit logging bypasses the shared `log_audit()` helper

Every other blueprint in the project (`devices_bp`, `formation_bp`, `Group_bp`, etc.) uses `util/audit.py`'s `log_audit(table_name, action_type, old_data, new_data, record_id=...)`. This file instead does its own raw `INSERT INTO payment_session_audit (action_type, old_data, new_data)`. Consequences:
- No `record_id` is stored, unlike the shared helper's pattern of including it when available — if `payment_session_audit`'s schema expects one (as other `*_audit` tables do), rows may be malformed or the sync pusher may not know which local record they refer to.
- If `log_audit()` was later hardened (e.g. the `LAST_INSERT_ID()` → `cursor.lastrowid` fix mentioned in other modules), this file won't benefit from it since it doesn't go through the shared path.
- `payment_bp` doesn't even import `log_audit` — worth confirming whether this was a deliberate divergence or just missed when the shared helper was introduced.

## TODO / cleanup candidates

- Fix the missing comma in `get_invoice_by_id` (this is a hard blocker — the endpoint cannot currently succeed).
- Decide the real intent of `get_payment_session`'s `GROUP BY` and fix accordingly (drop it, or add proper aggregates).
- Migrate `update_payment_session` and `update_payment_session_user` to use `log_audit()` for consistency with the rest of the codebase, including `record_id=payment_id`.
- Standardize route declarations to always include explicit `methods=['GET']` (currently `get_payment_session_user` omits it, relying on Flask's default).