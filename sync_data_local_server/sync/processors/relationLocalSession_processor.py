"""
RelationLocalSession Data Processor
Handles inserting and updating RelationLocalSession records in the database
"""

import sys
import os
from utils.helpers import format_date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def insert_relation_local_session(db, relation_data):
    """
    Handle 'created' relation_local_session records from API
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
            print("   ℹ️  No RelationLocalSession records in 'created'")
            return result

        print(f"   Processing {len(created_records)} relation_local_session record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM relation_local_session WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (record_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_records)}] RelationLocalSession ID {record_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                # Prepare new data with safe defaults — snake_case DB columns
                new_data = {
                    "id_prod": record.get("id"),
                    "local_id": record.get("localId"),
                    "session_id": record.get("sessionId"),
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "created_at": format_date(record.get("createdAt")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                # Check if record exists by id
                select_query = "SELECT * FROM relation_local_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] RelationLocalSession ID {record_id}...")

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
                        UPDATE relation_local_session SET
                            id_prod = %s,
                            local_id = %s,
                            session_id = %s,
                            enabled = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["local_id"],
                        new_data["session_id"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ✨ New relation_local_session - inserting...")

                    insert_query = """
                        INSERT INTO relation_local_session (
                            id, id_prod, local_id, session_id,
                            enabled, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["local_id"],
                        new_data["session_id"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation_local_session ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_relation_local_session: {err}")

    return result


def update_relation_local_session(db, relation_data):
    """
    Handle 'updated' relation_local_session records from API
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
            print("   ℹ️  No RelationLocalSession records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} relation_local_session record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                new_data = {
                    "id_prod": record.get("id"),
                    "local_id": record.get("localId"),
                    "session_id": record.get("sessionId"),
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "updated_at": format_date(record.get("updatedAt")),
                }

                check_prod_query = "SELECT * FROM relation_local_session WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (record_id,))

                if not existing_records:
                    select_query = "SELECT * FROM relation_local_session WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] RelationLocalSession ID {record_id}...")

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
                        UPDATE relation_local_session SET
                            id_prod = %s,
                            local_id = %s,
                            session_id = %s,
                            enabled = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["local_id"],
                        new_data["session_id"],
                        new_data["enabled"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ⚠️  RelationLocalSession not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO relation_local_session (
                            id, id_prod, local_id, session_id,
                            enabled, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["local_id"],
                        new_data["session_id"],
                        new_data["enabled"],
                        new_data["updated_at"],  # used as created_at too
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation_local_session ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_relation_local_session: {err}")

    return result


def process_relation_local_session(db, relation_data):
    """
    Process RelationLocalSession data (handles both 'created' and 'updated' sections)
    """
    print("\n📌 PROCESSING RELATION LOCAL SESSION")
    print("=" * 60)

    results = {
        "created_relation_local_session": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_relation_local_session": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if relation_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(relation_data['created'])} record(s)...")
        results["created_relation_local_session"] = insert_relation_local_session(db, relation_data)

    if relation_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(relation_data['updated'])} record(s)...")
        results["updated_relation_local_session"] = update_relation_local_session(db, relation_data)

    total_inserted = results["created_relation_local_session"]["inserted"] + results["updated_relation_local_session"]["inserted"]
    total_updated = results["created_relation_local_session"]["updated"] + results["updated_relation_local_session"]["updated"]
    total_skipped = results["created_relation_local_session"]["skipped"] + results["updated_relation_local_session"]["skipped"]
    total_errors = results["created_relation_local_session"]["errors"] + results["updated_relation_local_session"]["errors"]

    print("\n" + "=" * 60)
    print("📊 RELATION LOCAL SESSION - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results