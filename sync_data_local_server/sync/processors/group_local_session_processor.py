"""
Group Data Processor
Handles inserting and updating group records in relation_group_local_session table
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_groups(db, group_data):
    """
    Handle 'created' groups from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        group_data: Dictionary with 'created' key

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
        created_groups = group_data.get("created", [])
        result["total_processed"] = len(created_groups)

        if not created_groups:
            print("   ℹ️  No groups in 'created'")
            return result

        print(f"   Processing {len(created_groups)} group(s) from 'created'...")

        for i, group in enumerate(created_groups, 1):
            try:
                group_id = group.get("id")
                if not group_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "session_id": group.get("sessionId"),
                    "local_id": group.get("localId"),
                    "account_id": group.get("accountId"),
                    "name": group.get("name", ""),
                    "capacity": group.get("capacity"),
                    "status": 1 if group.get("status", True) else 0,
                    "enabled": 1 if group.get("enabled", True) else 0,
                    "special_group": 1 if group.get("special_group") else 0 if group.get("special_group") is not None else None,
                    "access_type": 1 if group.get("access_type") else 0 if group.get("access_type") is not None else None,
                    "releaseToken": 1 if group.get("releaseToken", False) else 0,
                    "useToken": group.get("useToken"),
                    "timestamp": format_date(group.get("timestamp")),
                    "created_at": format_date(group.get("createdAt")),
                    "updated_at": format_date(group.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM relation_group_local_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (group_id,))

                print(f"   [{i}/{len(created_groups)}] Group ID {group_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
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

                    # Data is different - UPDATE
                    print(f"      🔄 Already exists but data changed - updating...")

                    update_query = """
                        UPDATE relation_group_local_session SET
                            session_id = %s,
                            local_id = %s,
                            account_id = %s,
                            name = %s,
                            capacity = %s,
                            status = %s,
                            enabled = %s,
                            special_group = %s,
                            access_type = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s,
                            is_sync = 1
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["session_id"],
                        new_data["local_id"],
                        new_data["account_id"],
                        new_data["name"],
                        new_data["capacity"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["special_group"],
                        new_data["access_type"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        group_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO relation_group_local_session (
                            id, session_id, local_id, account_id, name, capacity, status, enabled,
                            special_group, access_type, releaseToken, useToken, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        group_id,
                        new_data["session_id"],
                        new_data["local_id"],
                        new_data["account_id"],
                        new_data["name"],
                        new_data["capacity"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["special_group"],
                        new_data["access_type"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing group ID {group.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_groups: {err}")

    return result


def update_groups(db, group_data):
    """
    Handle 'updated' groups from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        group_data: Dictionary with 'updated' key

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
        updated_groups = group_data.get("updated", [])
        result["total_processed"] = len(updated_groups)

        if not updated_groups:
            print("   ℹ️  No groups in 'updated'")
            return result

        print(f"   Processing {len(updated_groups)} group(s) from 'updated'...")

        for i, group in enumerate(updated_groups, 1):
            try:
                group_id = group.get("id")
                if not group_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "session_id": group.get("sessionId"),
                    "local_id": group.get("localId"),
                    "account_id": group.get("accountId"),
                    "name": group.get("name", ""),
                    "capacity": group.get("capacity"),
                    "status": 1 if group.get("status", True) else 0,
                    "enabled": 1 if group.get("enabled", True) else 0,
                    "special_group": 1 if group.get("special_group") else 0 if group.get("special_group") is not None else None,
                    "access_type": 1 if group.get("access_type") else 0 if group.get("access_type") is not None else None,
                    "releaseToken": 1 if group.get("releaseToken", False) else 0,
                    "useToken": group.get("useToken"),
                    "timestamp": format_date(group.get("timestamp")),
                    "updated_at": format_date(group.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM relation_group_local_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (group_id,))

                print(f"   [{i}/{len(updated_groups)}] Group ID {group_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
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

                    # Data is different - UPDATE
                    print(f"      🔄 Data changed - updating...")

                    update_query = """
                        UPDATE relation_group_local_session SET
                            session_id = %s,
                            local_id = %s,
                            account_id = %s,
                            name = %s,
                            capacity = %s,
                            status = %s,
                            enabled = %s,
                            special_group = %s,
                            access_type = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            updated_at = %s,
                            is_sync = 1
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["session_id"],
                        new_data["local_id"],
                        new_data["account_id"],
                        new_data["name"],
                        new_data["capacity"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["special_group"],
                        new_data["access_type"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        group_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO relation_group_local_session (
                            id, session_id, local_id, account_id, name, capacity, status, enabled,
                            special_group, access_type, releaseToken, useToken, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        group_id,
                        new_data["session_id"],
                        new_data["local_id"],
                        new_data["account_id"],
                        new_data["name"],
                        new_data["capacity"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["special_group"],
                        new_data["access_type"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing group ID {group.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_groups: {err}")

    return result


def process_groups(db, group_data):
    """
    Process group data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        group_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING GROUPS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if group_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(group_data['created'])} records)...")
        results["created_section"] = insert_groups(db, group_data)

    # Process 'updated' section
    if group_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(group_data['updated'])} records)...")
        results["updated_section"] = update_groups(db, group_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 GROUPS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results