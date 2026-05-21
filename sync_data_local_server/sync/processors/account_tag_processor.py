"""
Account Tag Data Processor
Handles inserting and updating account_tag records in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_account_tag(db, tag_data):
    """
    Handle 'created' account_tag records from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        tag_data: Dictionary with 'created' key

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
        created_records = tag_data.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No account_tag records in 'created'")
            return result

        print(f"   Processing {len(created_records)} account_tag record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data — map API fields → DB columns
                new_data = {
                    "account_id":    record.get("accountId"),
                    "tag_config_id": record.get("tagConfigId"),
                    "status":        1 if record.get("status") else 0,
                    "description":   record.get("description"),
                    "other_tag":     record.get("other_tag"),
                    "public":        1 if record.get("public") else 0,
                    "enabled":       1 if record.get("enabled") else 0,
                    "timestamp":     format_date(record.get("timestamp")),
                    "created_at":    format_date(record.get("createdAt")),
                    "updated_at":    format_date(record.get("updatedAt")),
                }

                # Check if record exists
                select_query = "SELECT * FROM account_tag WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] Account Tag ID {record_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
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
                        UPDATE account_tag SET
                            account_id    = %s,
                            tag_config_id = %s,
                            status        = %s,
                            description   = %s,
                            other_tag     = %s,
                            public        = %s,
                            enabled       = %s,
                            timestamp     = %s,
                            created_at    = %s,
                            updated_at    = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["tag_config_id"],
                        new_data["status"],
                        new_data["description"],
                        new_data["other_tag"],
                        new_data["public"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO account_tag (
                            id, account_id, tag_config_id, status, description,
                            other_tag, public, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["account_id"],
                        new_data["tag_config_id"],
                        new_data["status"],
                        new_data["description"],
                        new_data["other_tag"],
                        new_data["public"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account_tag ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_account_tag: {err}")

    return result


def update_account_tag(db, tag_data):
    """
    Handle 'updated' account_tag records from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

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
            print("   ℹ️  No account_tag records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} account_tag record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data — map API fields → DB columns
                new_data = {
                    "account_id":    record.get("accountId"),
                    "tag_config_id": record.get("tagConfigId"),
                    "status":        1 if record.get("status") else 0,
                    "description":   record.get("description"),
                    "other_tag":     record.get("otherTag"),
                    "public":        1 if record.get("public") else 0,
                    "enabled":       1 if record.get("enabled") else 0,
                    "timestamp":     format_date(record.get("timestamp")),
                    "updated_at":    format_date(record.get("updatedAt")),
                }

                # Check if record exists
                select_query = "SELECT * FROM account_tag WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] Account Tag ID {record_id}...")

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
                        UPDATE account_tag SET
                            account_id    = %s,
                            tag_config_id = %s,
                            status        = %s,
                            description   = %s,
                            other_tag     = %s,
                            public        = %s,
                            enabled       = %s,
                            timestamp     = %s,
                            updated_at    = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["tag_config_id"],
                        new_data["status"],
                        new_data["description"],
                        new_data["other_tag"],
                        new_data["public"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO account_tag (
                            id, account_id, tag_config_id, status, description,
                            other_tag, public, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["account_id"],
                        new_data["tag_config_id"],
                        new_data["status"],
                        new_data["description"],
                        new_data["other_tag"],
                        new_data["public"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],   # fallback for created_at
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account_tag ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_account_tag: {err}")

    return result


def processor_account_tag(db, tag_data):
    """
    Process account_tag data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        tag_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n🏷️  PROCESSING ACCOUNT TAG")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if tag_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(tag_data['created'])} records)...")
        results["created_section"] = insert_account_tag(db, tag_data)

    # Process 'updated' section
    if tag_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(tag_data['updated'])} records)...")
        results["updated_section"] = update_account_tag(db, tag_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 ACCOUNT TAG - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results