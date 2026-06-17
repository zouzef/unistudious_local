"""
Relation Completion tag Data Processor
Handles inserting and updating relation_completion_tag records in the database
"""

import sys
import os
from utils.helpers import format_date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def insert_relationCompletion_tag(db, tag_data):
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }
    try:
        created_records = tag_data.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No relation_completion_tag records in 'created'")
            return result

        print(f"     Processing {len(created_records)} relation_completion_tag record(s) from 'created' ...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM relation_completion_tag WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (record_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_records)}] Relation Completion Tag ID {record_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                # Prepare new data — map API fields → DB columns
                new_data = {
                    "id_prod": record_id,
                    "account_id": record.get("accountId"),
                    "calander_group_id": record.get("calanderId"),
                    "tag_id": record.get("accountCompletionTagId"),
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "release_token": 1 if record.get("releaseToken") else 0,
                    "use_token": record.get("useToken"),
                    "timestamp": format_date(record.get("timestamp")),
                    "created_at": format_date(record.get("createdAt")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                # Check if record exists by id
                select_query = "SELECT * FROM relation_completion_tag WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] Relation Completion Tag ID {record_id}...")

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
                        UPDATE relation_completion_tag SET 
                            id_prod             = %s,
                            tag_id              = %s,
                            account_id          = %s,
                            calander_group_id   = %s,
                            enabled             = %s,
                            release_token       = %s,
                            use_token           = %s,
                            timestamp           = %s,
                            created_at          = %s,
                            updated_at          = %s
                        WHERE id = %s
                    """
                    db.execute_query(update_query, (
                        new_data['id_prod'],
                        new_data['tag_id'],
                        new_data['account_id'],
                        new_data['calander_group_id'],
                        new_data['enabled'],
                        new_data['release_token'],
                        new_data['use_token'],
                        new_data['timestamp'],
                        new_data['created_at'],
                        new_data['updated_at'],
                        record_id
                    ))
                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")
                else:
                    print(f"      ✨ New record - inserting...")
                    insert_query = """
                        INSERT INTO relation_completion_tag(
                            id, id_prod, account_id, calander_group_id, tag_id, enabled, created_at,
                            timestamp, updated_at, release_token, use_token
                        )VALUES(
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                    """
                    db.execute_query(insert_query, (
                        record_id,
                        new_data['id_prod'],
                        new_data['account_id'],
                        new_data['calander_group_id'],
                        new_data['tag_id'],
                        new_data['enabled'],
                        new_data['created_at'],
                        new_data['timestamp'],
                        new_data['updated_at'],
                        new_data['release_token'],
                        new_data['use_token']
                    ))
                    result['inserted'] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation_completion_tag ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")
    except Exception as err:
        print(f"   💥 Unexpected error in relation_completion_tag: {err}")

    return result


def update_relationCompletion_tag(db, tag_data):
    """
    Handle 'updated' relation_completion_tag records from API
    Logic:
    - Look up by id_prod first, then by id
    - If exists → UPDATE (using local id)
    - If not → INSERT (don't skip!)

    Args:
        db: Database instance
        tag_data: Dictionary with 'updated' key

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
        updated_records = tag_data.get("updated", [])
        result["total_processed"] = len(updated_records)

        if not updated_records:
            print("   ℹ️  No relationCompletionTag records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} relationCompletionTag record(s) from 'updated'...")
        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data — map API fields → DB columns
                new_data = {
                    "id_prod": record_id,
                    "account_id": record.get("accountId"),
                    "calander_group_id": record.get("calanderId"),
                    "tag_id": record.get("accountCompletionTagId"),
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "release_token": 1 if record.get("releaseToken") else 0,
                    "use_token": record.get("useToken"),
                    "timestamp": format_date(record.get("timestamp")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                check_prod_query = "SELECT * FROM relation_completion_tag WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (record_id,))

                if not existing_records:
                    select_query = "SELECT * FROM relation_completion_tag WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] Completion Tag Account ID {record_id}...")

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
                        print("      ⏭️  Data is identical - skipped")
                        result["skipped"] += 1
                        continue

                    print(f"      🔄 Data changed - updating...")

                    update_query = """
                        UPDATE relation_completion_tag SET 
                            id_prod               = %s,
                            tag_id                = %s,
                            account_id            = %s,
                            calander_group_id     = %s,
                            enabled               = %s,
                            timestamp             = %s,
                            updated_at            = %s,
                            release_token         = %s,
                            use_token              = %s
                        WHERE id = %s
                    """
                    db.execute_query(update_query, (
                        new_data['id_prod'],
                        new_data['tag_id'],
                        new_data['account_id'],
                        new_data['calander_group_id'],
                        new_data['enabled'],
                        new_data['timestamp'],
                        new_data['updated_at'],
                        new_data['release_token'],
                        new_data['use_token'],
                        existing["id"]
                    ))
                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")
                else:
                    print(f"      ⚠️  Record not found in DB - inserting...")
                    insert_query = """
                        INSERT INTO relation_completion_tag(
                            id, id_prod, account_id, calander_group_id, tag_id,
                            enabled, release_token, use_token, timestamp,
                            created_at, updated_at
                        )VALUES(
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    db.execute_query(insert_query, (
                        record_id,
                        new_data['id_prod'],
                        new_data['account_id'],
                        new_data['calander_group_id'],
                        new_data['tag_id'],
                        new_data['enabled'],
                        new_data['release_token'],
                        new_data['use_token'],
                        new_data['timestamp'],
                        new_data['updated_at'],  # used as created_at too
                        new_data['updated_at']
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relationCompletionTag ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue
    except Exception as err:
        print(f"   💥 Unexpected error in update_relationCompletionTag: {err}")

    return result


def processor_relationCompletionTag(db, tag_data):
    """
    Process relation_completion_tag data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        tag_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """

    print("\n📌 PROCESSING RELATION COMPLETION TAG")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if tag_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(tag_data['created'])} records)...")
        results["created_section"] = insert_relationCompletion_tag(db, tag_data)

    if tag_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(tag_data['updated'])} records)...")
        results["updated_section"] = update_relationCompletion_tag(db, tag_data)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 RELATION COMPLETION TAG - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results