"""
RelationTeacherAccount Data Processor
Handles inserting and updating RelationTeacherAccount records in the database

NOTE: Table schema was not provided for this entity. Columns below were
inferred directly from the API payload (see fields in `new_data`). Please
verify column names/types against the real `relation_teacher_account` table
(e.g. via `DESCRIBE relation_teacher_account;`) and adjust if needed —
especially:
  - access_permissions: assumed JSON/TEXT column (stores JSON-encoded list)
  - status / enabled: assumed TINYINT(1)
  - release_token: assumed TINYINT(1)
"""

import sys
import os
import json
from utils.helpers import format_date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def insert_relation_teacher_account(db, relation_data):
    """
    Handle 'created' relation_teacher_account records from API
    Logic:
    - Check if id_prod already exists (avoid duplicates from local pushes)
    - If record exists in DB by id → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        relation_data: Dictionary with 'created' key

    Returns:
        dict: Statistics (inserted, updated, skipped, errors)
    """
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        created_records = relation_data.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No RelationTeacherAccount records in 'created'")
            return result

        print(f"   Processing {len(created_records)} relation_teacher_account record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM relation_teacher_account WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (record_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_records)}] RelationTeacherAccount ID {record_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                # Prepare new data with safe defaults — snake_case DB columns
                # TODO: confirm column names/types against `DESCRIBE relation_teacher_account;`
                access_permissions = record.get("accessPermissions")
                new_data = {
                    "id_prod": record.get("id"),
                    "uuid": record.get("uuid"),
                    "status": 1 if record.get("status", True) else 0,
                    "access_permissions": json.dumps(access_permissions) if access_permissions is not None else None,
                    "access_session": json.dumps(record.get("accessSession")) if record.get("accessSession") is not None else None,
                    "invitation_relation_teacher_account_id": record.get("invitationRelationTeacherAccountId"),
                    "cloud_path": record.get("cloudPath"),
                    "user_id": record.get("teacherId"),
                    "release_token": 1 if record.get("releaseToken", False) else 0,
                    "use_token": record.get("useToken"),
                    "created_at": format_date(record.get("createdAt")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                # Check if record exists by id
                select_query = "SELECT * FROM relation_teacher_account WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] RelationTeacherAccount ID {record_id}...")

                if existing_records:
                    existing = existing_records[0]

                    has_changes = False
                    for key, value in new_data.items():
                        old_value = str(existing.get(key)) if existing.get(key) is not None else None
                        new_value = str(value) if value is not None else None
                        if old_value != new_value:
                            has_changes = True
                            break

                    if not has_changes:
                        print(f"      ⏭️  Already exists with same data - skipped")
                        result["skipped"] += 1
                        continue

                    print(f"      🔄 Already exists but data changed - updating...")

                    update_query = """
                        UPDATE relation_teacher_account SET
                            id_prod = %s,
                            uuid = %s,
                            status = %s,
                            access_permissions = %s,
                            access_session = %s,
                            invitation_relation_teacher_account_id = %s,
                            cloud_path = %s,
                            user_id = %s,
                            release_token = %s,
                            use_token = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["uuid"],
                        new_data["status"],
                        new_data["access_permissions"],
                        new_data["access_session"],
                        new_data["invitation_relation_teacher_account_id"],
                        new_data["cloud_path"],
                        new_data["user_id"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ✨ New relation_teacher_account - inserting...")

                    insert_query = """
                        INSERT INTO relation_teacher_account (
                            id, id_prod, uuid, status, access_permissions,
                            access_session, invitation_relation_teacher_account_id,
                            cloud_path, user_id, release_token, use_token,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["uuid"],
                        new_data["status"],
                        new_data["access_permissions"],
                        new_data["access_session"],
                        new_data["invitation_relation_teacher_account_id"],
                        new_data["cloud_path"],
                        new_data["user_id"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation_teacher_account ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_relation_teacher_account: {err}")

    return result


def update_relation_teacher_account(db, relation_data):
    """
    Handle 'updated' relation_teacher_account records from API
    Logic:
    - Look up by id_prod first, then by id
    - If exists → UPDATE (using local id)
    - If not → INSERT (don't skip!)

    Args:
        db: Database instance
        relation_data: Dictionary with 'updated' key

    Returns:
        dict: Statistics (inserted, updated, skipped, errors)
    """
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        updated_records = relation_data.get("updated", [])
        result["total_processed"] = len(updated_records)

        if not updated_records:
            print("   ℹ️  No RelationTeacherAccount records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} relation_teacher_account record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                access_permissions = record.get("accessPermissions")
                new_data = {
                    "id_prod": record.get("id"),
                    "uuid": record.get("uuid"),
                    "status": 1 if record.get("status", True) else 0,
                    "access_permissions": json.dumps(access_permissions) if access_permissions is not None else None,
                    "access_session": json.dumps(record.get("accessSession")) if record.get("accessSession") is not None else None,
                    "invitation_relation_teacher_account_id": record.get("invitationRelationTeacherAccountId"),
                    "cloud_path": record.get("cloudPath"),
                    "user_id": record.get("teacherId"),
                    "release_token": 1 if record.get("releaseToken", False) else 0,
                    "use_token": record.get("useToken"),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                check_prod_query = "SELECT * FROM relation_teacher_account WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (record_id,))

                if not existing_records:
                    select_query = "SELECT * FROM relation_teacher_account WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] RelationTeacherAccount ID {record_id}...")

                if existing_records:
                    existing = existing_records[0]

                    has_changes = False
                    for key, value in new_data.items():
                        old_value = str(existing.get(key)) if existing.get(key) is not None else None
                        new_value = str(value) if value is not None else None
                        if old_value != new_value:
                            has_changes = True
                            break

                    if not has_changes:
                        print(f"      ⏭️  Data is identical - skipped")
                        result["skipped"] += 1
                        continue

                    print(f"      🔄 Data changed - updating...")

                    update_query = """
                        UPDATE relation_teacher_account SET
                            id_prod = %s,
                            uuid = %s,
                            status = %s,
                            access_permissions = %s,
                            access_session = %s,
                            invitation_relation_teacher_account_id = %s,
                            cloud_path = %s,
                            user_id = %s,
                            release_token = %s,
                            use_token = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["uuid"],
                        new_data["status"],
                        new_data["access_permissions"],
                        new_data["access_session"],
                        new_data["invitation_relation_teacher_account_id"],
                        new_data["cloud_path"],
                        new_data["user_id"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ⚠️  RelationTeacherAccount not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO relation_teacher_account (
                            id, id_prod, uuid, status, access_permissions,
                            access_session, invitation_relation_teacher_account_id,
                            cloud_path, user_id, release_token, use_token,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["uuid"],
                        new_data["status"],
                        new_data["access_permissions"],
                        new_data["access_session"],
                        new_data["invitation_relation_teacher_account_id"],
                        new_data["cloud_path"],
                        new_data["user_id"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["updated_at"],  # used as created_at too
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation_teacher_account ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_relation_teacher_account: {err}")

    return result


def process_relation_teacher_account(db, relation_data):
    """
    Process RelationTeacherAccount data (handles both 'created' and 'updated' sections)
    """
    print("\n📌 PROCESSING RELATION TEACHER ACCOUNT")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if relation_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(relation_data['created'])} record(s)...")
        results["created_section"] = insert_relation_teacher_account(db, relation_data)

    if relation_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(relation_data['updated'])} record(s)...")
        results["updated_section"] = update_relation_teacher_account(db, relation_data)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 RELATION TEACHER ACCOUNT - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results