"""
Level Config Data Processor
Handles inserting and updating level_config records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_levels(db, level_data):
    """
    Handle 'created' levels from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        level_data: Dictionary with 'created' key

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
        created_levels = level_data.get("created", [])
        result["total_processed"] = len(created_levels)

        if not created_levels:
            print("   ℹ️  No levels in 'created'")
            return result

        print(f"   Processing {len(created_levels)} level(s) from 'created'...")

        for i, level in enumerate(created_levels, 1):
            try:
                level_id = level.get("id")
                if not level_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "name": level.get("name", ""),
                    "description": level.get("description"),
                    "status": 1 if level.get("status", True) else 0,
                    "enabled": 1 if level.get("enabled", True) else 0,
                    "timestamp": format_date(level.get("timestamp")),
                    "created_at": format_date(level.get("createdAt")),
                    "updated_at": format_date(level.get("updatedAt")),
                }

                # Check if record exists
                select_query = "SELECT * FROM level_config WHERE id = %s"
                existing_records = db.fetch_query(select_query, (level_id,))

                print(f"   [{i}/{len(created_levels)}] Level ID {level_id}...")

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
                        UPDATE level_config SET
                            name = %s,
                            description = %s,
                            status = %s,
                            enabled = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """
                    db.execute_query(update_query, (
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        level_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO level_config (
                            id, name, description, status, enabled,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    db.execute_query(insert_query, (
                        level_id,
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing level ID {level.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_levels: {err}")

    return result


def update_levels(db, level_data):
    """
    Handle 'updated' levels from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        level_data: Dictionary with 'updated' key

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
        updated_levels = level_data.get("updated", [])
        result["total_processed"] = len(updated_levels)

        if not updated_levels:
            print("   ℹ️  No levels in 'updated'")
            return result

        print(f"   Processing {len(updated_levels)} level(s) from 'updated'...")

        for i, level in enumerate(updated_levels, 1):
            try:
                level_id = level.get("id")
                if not level_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "name": level.get("name", ""),
                    "description": level.get("description"),
                    "status": 1 if level.get("status", True) else 0,
                    "enabled": 1 if level.get("enabled", True) else 0,
                    "timestamp": format_date(level.get("timestamp")),
                    "updated_at": format_date(level.get("updatedAt")),
                }

                # Check if record exists
                select_query = "SELECT * FROM level_config WHERE id = %s"
                existing_records = db.fetch_query(select_query, (level_id,))

                print(f"   [{i}/{len(updated_levels)}] Level ID {level_id}...")

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
                        print(f"      ⏭️  Data is identical - skipped")
                        result["skipped"] += 1
                        continue

                    print(f"      🔄 Data changed - updating...")

                    update_query = """
                        UPDATE level_config SET
                            name = %s,
                            description = %s,
                            status = %s,
                            enabled = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """
                    db.execute_query(update_query, (
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        level_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO level_config (
                            id, name, description, status, enabled,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    # Use updated_at as created_at fallback
                    db.execute_query(insert_query, (
                        level_id,
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # fallback for created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing level ID {level.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_levels: {err}")

    return result


def processor_level_session(db, level_data):
    """
    Process level_config data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        level_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING LEVEL CONFIG")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if level_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(level_data['created'])} records)...")
        results["created_section"] = insert_levels(db, level_data)

    # Process 'updated' section
    if level_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(level_data['updated'])} records)...")
        results["updated_section"] = update_levels(db, level_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 LEVEL CONFIG - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results