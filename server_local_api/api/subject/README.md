# Subject Blueprint (`subject_bp`)

Flask blueprint for `unistudious_local`, mounted at `/scl`. Manages **account subjects** (`account_subject`) — an account's chosen subjects, each either tied to a global `subject_config` entry or a free-text `other_subject`. Create/update/delete all log to `account_subject_audit` via `log_audit()`.

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/scl/get_sub_subjects` | List all enabled account-subjects globally, resolved to a display name — **see known issue #1** |
| GET | `/scl/get_subject_config` | List all enabled global subject configs (not account-scoped) |
| GET | `/scl/get_account_subject/<account_id>` | List an account's subjects — **see known issue #1** |
| GET | `/scl/view_account_subject/<account_subject_id>` | View one account-subject — **see known issue #1** |
| POST | `/scl/create_account_subject/<account_id>` | Create an account-subject |
| POST | `/scl/update_account_subject/<account_subject_id>` | Update an account-subject |
| POST | `/scl/delete_account_subject/<account_subject_id>` | Soft-delete (`enabled = 0`) |

## The "other subject" pattern

`account_subject` supports two ways of naming a subject:
- **Linked**: `subject_config_id` points to a row in `subject_config`, and the name comes from there.
- **Custom**: `other_subject` holds free text directly, with `subject_config_id` presumably `NULL`.

Every read endpoint resolves this with the same `CASE` pattern:

```sql
CASE 
    WHEN a.other_subject IS NOT NULL THEN a.other_subject
    ELSE sc.name
END AS subject_identifier
```

paired with a `LEFT JOIN subject_config sc ON sc.id = a.subject_config_id`, so that custom subjects (with no matching config row) still return a name.

## ⚠️ Known issue: the `LEFT JOIN` fallback is defeated by the `WHERE` clause

All three read endpoints that use this pattern — `get_sub_subjects`, `get_account_subject`, `view_account_subject` — also filter with:

```sql
WHERE ... AND sc.enabled = 1  -- (and sc.status = 1 in some endpoints)
```

Since a `LEFT JOIN` produces `NULL` for `sc.*` when there's no matching `subject_config` row (i.e. exactly the "custom subject" case the `CASE`/fallback was written to handle), the condition `sc.enabled = 1` evaluates to unknown/false for those rows and **filters them out entirely**. The net effect: the `LEFT JOIN` + `CASE` fallback never actually gets to run for genuinely custom subjects — any `account_subject` row with `other_subject` set and no linked `subject_config` silently disappears from all three of these endpoints.

**Fix:** move the `subject_config`-specific conditions into the `JOIN`'s `ON` clause instead of `WHERE`, so they only constrain the join itself and don't kill unmatched rows:

```sql
FROM account_subject a
LEFT JOIN subject_config sc 
    ON sc.id = a.subject_config_id AND sc.enabled = 1 AND sc.status = 1
WHERE a.enabled = 1 AND a.status = 1
```

This applies to all three affected endpoints (`get_sub_subjects`, `get_account_subject`, `view_account_subject`).

## Other observations

- **`delete_account_subject`'s route uses `<account_subject_id>` without a type converter** (`<int:account_subject_id>` everywhere else in this file). Flask will accept any string here, including non-numeric values, which then get passed straight into the query — worth aligning with the rest of the file for consistency and to fail fast on bad input.
- **`get_subject_config`'s 404 message says `"There is no subjects for this account"`**, but the endpoint takes no `account_id` and the query has no account scoping at all — it returns every enabled global subject config. The message is misleading; either the endpoint should genuinely be account-scoped, or the message should just say "no subjects found."

## TODO / cleanup candidates

- Move the `subject_config` enabled/status filters into the `ON` clause in `get_sub_subjects`, `get_account_subject`, and `view_account_subject` so custom (`other_subject`) rows stop disappearing.
- Add `<int:...>` typing to `delete_account_subject`'s route parameter.
- Either scope `get_subject_config` by account or fix its error message.