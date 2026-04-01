import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_slcs(db, slc_data):
    """
    Handle 'created' SLCs from API
    Logic:
    - If SLC exists in DB → UPDATE it
    - If SLC does NOT exist → INSERT it

    Args:
        db: Database instance
        slc_data: Dictionary with 'created' key

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
        created_slcs = slc_data.get("created", [])
        result["total_processed"] = len(created_slcs)

        if not created_slcs:
            print("   ℹ️  No SLCs in 'created'")
            return result

        print(f"   Processing {len(created_slcs)} SLC(s) from 'created'...")

        for i, slc in enumerate(created_slcs, 1):
            try:
                slc_id = slc.get("id")
                if not slc_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "uuid": slc.get("uuid"),
                    "username": slc.get("username"),
                    "slc_username": slc.get("slc_username"),
                    "slc_password": slc.get("slc_password"),
                    "account_id": slc.get("accountId"),
                    "timestamp": format_date(slc.get("timestamp")),
                    "created_at": format_date(slc.get("createdAt")),
                    "updated_at": format_date(slc.get("updatedAt"))
                }

                # Check if SLC exists
                select_query = "SELECT * FROM slc WHERE id = %s"
                existing_records = db.fetch_query(select_query, (slc_id,))

                print(f"   [{i}/{len(created_slcs)}] SLC ID {slc_id}...")

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

                    # ✅ FIX 1: Added missing comma after account_id = %s
                    update_query = """
                        UPDATE slc SET
                            uuid = %s,
                            username = %s,
                            slc_username = %s,
                            slc_password = %s,
                            account_id = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["uuid"],
                        new_data["username"],
                        new_data["slc_username"],
                        new_data["slc_password"],
                        new_data["account_id"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        slc_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New SLC - inserting...")

                    # ✅ FIX 2: Changed 8 placeholders to 9 to match 9 columns
                    insert_query = """
                        INSERT INTO slc (
                            id, uuid, username, slc_username, slc_password, account_id,
                            timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        slc_id,
                        new_data["uuid"],
                        new_data["username"],
                        new_data["slc_username"],
                        new_data["slc_password"],
                        new_data["account_id"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing SLC ID {slc.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_slcs: {err}")

    return result


def update_slcs(db, slc_data):
    """
    Handle 'updated' SLCs from API
    Logic:
    - If SLC exists in DB → UPDATE it
    - If SLC does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        slc_data: Dictionary with 'updated' key

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
        updated_slcs = slc_data.get("updated", [])
        result["total_processed"] = len(updated_slcs)

        if not updated_slcs:
            print("   ℹ️  No SLCs in 'updated'")
            return result

        print(f"   Processing {len(updated_slcs)} SLC(s) from 'updated'...")

        for i, slc in enumerate(updated_slcs, 1):
            try:
                slc_id = slc.get("id")
                if not slc_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIX 3: Added account_id to new_data so it gets saved
                new_data = {
                    "uuid": slc.get("uuid"),
                    "username": slc.get("username"),
                    "slc_username": slc.get("slc_username"),
                    "slc_password": slc.get("slc_password"),
                    "account_id": slc.get("accountId"),
                    "timestamp": format_date(slc.get("timestamp")),
                    "updated_at": format_date(slc.get("updatedAt"))
                }

                # Check if SLC exists
                select_query = "SELECT * FROM slc WHERE id = %s"
                existing_records = db.fetch_query(select_query, (slc_id,))

                print(f"   [{i}/{len(updated_slcs)}] SLC ID {slc_id}...")

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

                    # ✅ FIX 3 (cont): Added account_id to UPDATE query
                    update_query = """
                        UPDATE slc SET
                            uuid = %s,
                            username = %s,
                            slc_username = %s,
                            slc_password = %s,
                            account_id = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["uuid"],
                        new_data["username"],
                        new_data["slc_username"],
                        new_data["slc_password"],
                        new_data["account_id"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        slc_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  SLC not found in DB - inserting...")

                    # ✅ FIX 3 (cont): Added account_id to INSERT query
                    insert_query = """
                        INSERT INTO slc (
                            id, uuid, username, slc_username, slc_password, account_id,
                            timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        slc_id,
                        new_data["uuid"],
                        new_data["username"],
                        new_data["slc_username"],
                        new_data["slc_password"],
                        new_data["account_id"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing SLC ID {slc.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_slcs: {err}")

    return result


def process_slcs(db, slc_data):
    """
    Process SLC data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        slc_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING SLCS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if slc_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(slc_data['created'])} records)...")
        results["created_section"] = insert_slcs(db, slc_data)

    # Process 'updated' section
    if slc_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(slc_data['updated'])} records)...")
        results["updated_section"] = update_slcs(db, slc_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 SLCS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results