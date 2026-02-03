"""
Tablet Data Processor
Handles inserting and updating tablet records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_tablets(db, tablet_data):
    """
    Handle 'created' tablets from API
    Logic:
    - If tablet exists in DB → UPDATE it
    - If tablet does NOT exist → INSERT it

    Args:
        db: Database instance
        tablet_data: Dictionary with 'created' key

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
        created_tablets = tablet_data.get("created", [])
        result["total_processed"] = len(created_tablets)

        if not created_tablets:
            print("   ℹ️  No tablets in 'created'")
            return result

        print(f"   Processing {len(created_tablets)} tablet(s) from 'created'...")

        for i, tablet in enumerate(created_tablets, 1):
            try:
                tablet_id = tablet.get("id")
                if not tablet_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "slc_id": tablet.get("slcId"),
                    "room_id": tablet.get("roomId"),
                    "name": tablet.get("name", ""),
                    "mac_id": tablet.get("mac_id", ""),
                    "password": tablet.get("password", ""),
                    "status": tablet.get("status", "Active"),
                    "enabled": 1 if tablet.get("enabled", True) else 0,
                    "timestamp": format_date(tablet.get("timestamp")),
                    "created_at": format_date(tablet.get("createdAt")),
                    "updated_at": format_date(tablet.get("updatedAt"))
                }

                # Check if tablet exists
                select_query = "SELECT * FROM tablet WHERE id = %s"
                existing_records = db.fetch_query(select_query, (tablet_id,))

                print(f"   [{i}/{len(created_tablets)}] Tablet ID {tablet_id}...")

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
                        UPDATE tablet SET
                            slc_id = %s,
                            room_id = %s,
                            name = %s,
                            mac_id = %s,
                            password = %s,
                            status = %s,
                            enabled = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        tablet_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New tablet - inserting...")

                    insert_query = """
                        INSERT INTO tablet (
                            id, slc_id, room_id, name, mac_id, password,
                            status, enabled, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        tablet_id,
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing tablet ID {tablet.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_tablets: {err}")

    return result


def update_tablets(db, tablet_data):
    """
    Handle 'updated' tablets from API
    Logic:
    - If tablet exists in DB → UPDATE it
    - If tablet does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        tablet_data: Dictionary with 'updated' key

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
        updated_tablets = tablet_data.get("updated", [])
        result["total_processed"] = len(updated_tablets)

        if not updated_tablets:
            print("   ℹ️  No tablets in 'updated'")
            return result

        print(f"   Processing {len(updated_tablets)} tablet(s) from 'updated'...")

        for i, tablet in enumerate(updated_tablets, 1):
            try:
                tablet_id = tablet.get("id")
                if not tablet_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "slc_id": tablet.get("slcId"),
                    "room_id": tablet.get("roomId"),
                    "name": tablet.get("name", ""),
                    "mac_id": tablet.get("mac_id", ""),
                    "password": tablet.get("password", ""),
                    "status": tablet.get("status", "Active"),
                    "enabled": 1 if tablet.get("enabled", True) else 0,
                    "timestamp": format_date(tablet.get("timestamp")),
                    "updated_at": format_date(tablet.get("updatedAt"))
                }

                # Check if tablet exists
                select_query = "SELECT * FROM tablet WHERE id = %s"
                existing_records = db.fetch_query(select_query, (tablet_id,))

                print(f"   [{i}/{len(updated_tablets)}] Tablet ID {tablet_id}...")

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
                        UPDATE tablet SET
                            slc_id = %s,
                            room_id = %s,
                            name = %s,
                            mac_id = %s,
                            password = %s,
                            status = %s,
                            enabled = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        tablet_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Tablet not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO tablet (
                            id, slc_id, room_id, name, mac_id, password,
                            status, enabled, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        tablet_id,
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing tablet ID {tablet.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_tablets: {err}")

    return result


def process_tablets(db, tablet_data):
    """
    Process tablet data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        tablet_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING TABLETS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if tablet_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(tablet_data['created'])} records)...")
        results["created_section"] = insert_tablets(db, tablet_data)

    # Process 'updated' section
    if tablet_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(tablet_data['updated'])} records)...")
        results["updated_section"] = update_tablets(db, tablet_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 TABLETS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results