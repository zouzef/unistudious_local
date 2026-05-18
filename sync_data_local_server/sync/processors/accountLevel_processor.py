"""
Account Level Data Processor
Handles inserting and updating account_level records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_account_levels(db, account_level_data):
    """
    Handle 'created' account levels from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        account_level_data: Dictionary with 'created' key

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
        created_account_levels = account_level_data.get("created", [])
        result["total_processed"] = len(created_account_levels)

        if not created_account_levels:
            print("   ℹ️  No account levels in 'created'")
            return result

        print(f"   Processing {len(created_account_levels)} account level(s) from 'created'...")

        for i, account_level in enumerate(created_account_levels, 1):
            try:
                account_level_id = account_level.get("id")
                if not account_level_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "account_id": account_level.get("accountId"),
                    "level_config_id": account_level.get("levelConfigId"),
                    "other_level": account_level.get("otherLevel"),
                    "description": account_level.get("description", ""),
                    "status": 1 if account_level.get("status", True) else 0,
                    "enabled": 1 if account_level.get("enabled", True) else 0,
                    "release_token": 1 if account_level.get("releaseToken", False) else 0,
                    "use_token": account_level.get("useToken"),
                    "timestamp": format_date(account_level.get("timestamp")),
                    "created_at": format_date(account_level.get("createdAt")),
                    "updated_at": format_date(account_level.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM account_level WHERE id = %s"
                existing_records = db.fetch_query(select_query, (account_level_id,))

                print(f"   [{i}/{len(created_account_levels)}] Account Level ID {account_level_id}...")

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
                        UPDATE account_level SET
                            account_id = %s,
                            level_config_id = %s,
                            other_level = %s,
                            description = %s,
                            status = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s,
                            
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["level_config_id"],
                        new_data["other_level"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        account_level_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO account_level (
                            id, account_id, level_config_id, other_level, description,
                            status, enabled, release_token, use_token,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        account_level_id,
                        new_data["account_id"],
                        new_data["level_config_id"],
                        new_data["other_level"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account level ID {account_level.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_account_levels: {err}")

    return result


def update_account_levels(db, account_level_data):
    """
    Handle 'updated' account levels from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        account_level_data: Dictionary with 'updated' key

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
        updated_account_levels = account_level_data.get("updated", [])
        result["total_processed"] = len(updated_account_levels)

        if not updated_account_levels:
            print("   ℹ️  No account levels in 'updated'")
            return result

        print(f"   Processing {len(updated_account_levels)} account level(s) from 'updated'...")

        for i, account_level in enumerate(updated_account_levels, 1):
            try:
                account_level_id = account_level.get("id")
                if not account_level_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "account_id": account_level.get("accountId"),
                    "level_config_id": account_level.get("levelConfigId"),
                    "other_level": account_level.get("otherLevel"),
                    "description": account_level.get("description", ""),
                    "status": 1 if account_level.get("status", True) else 0,
                    "enabled": 1 if account_level.get("enabled", True) else 0,
                    "release_token": 1 if account_level.get("releaseToken", False) else 0,
                    "use_token": account_level.get("useToken"),
                    "timestamp": format_date(account_level.get("timestamp")),
                    "updated_at": format_date(account_level.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM account_level WHERE id = %s"
                existing_records = db.fetch_query(select_query, (account_level_id,))

                print(f"   [{i}/{len(updated_account_levels)}] Account Level ID {account_level_id}...")

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
                        UPDATE account_level SET
                            account_id = %s,
                            level_config_id = %s,
                            other_level = %s,
                            description = %s,
                            status = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            timestamp = %s,
                            updated_at = %s,
                            
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["level_config_id"],
                        new_data["other_level"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        account_level_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO account_level (
                            id, account_id, level_config_id, other_level, description,
                            status, enabled, release_token, use_token,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        account_level_id,
                        new_data["account_id"],
                        new_data["level_config_id"],
                        new_data["other_level"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account level ID {account_level.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_account_levels: {err}")

    return result


def processor_account_level(db, account_level_data):
    """
    Process account level data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        account_level_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING ACCOUNT LEVELS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if account_level_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(account_level_data['created'])} records)...")
        results["created_section"] = insert_account_levels(db, account_level_data)

    # Process 'updated' section
    if account_level_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(account_level_data['updated'])} records)...")
        results["updated_section"] = update_account_levels(db, account_level_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 ACCOUNT LEVELS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results