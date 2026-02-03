"""
Attendance Data Processor
Handles inserting and updating attendance records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_attendances(db, attendance_data):
    """
    Handle 'created' attendances from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        attendance_data: Dictionary with 'created' key

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
        created_attendances = attendance_data.get("created", [])
        result["total_processed"] = len(created_attendances)

        if not created_attendances:
            print("   ℹ️  No attendances in 'created'")
            return result

        print(f"   Processing {len(created_attendances)} attendance(s) from 'created'...")

        for i, attendance in enumerate(created_attendances, 1):
            try:
                attendance_id = attendance.get("id")
                if not attendance_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "user_id": attendance.get("userId"),
                    "account_id": attendance.get("accountId"),
                    "calander_id": attendance.get("calenderId"),
                    "session_id": attendance.get("sessionId"),
                    "group_session_id": attendance.get("groupId"),
                    "is_present": 1 if attendance.get("present", False) else 0,
                    "day": format_date(attendance.get("day")),
                    "note": attendance.get("note"),
                    "is_editable": 1 if attendance.get("editable", True) else 0,
                    "enabled": 1 if attendance.get("enabled", True) else 0,
                    "releaseToken": 1 if attendance.get("releaseToken", False) else 0,
                    "useToken": attendance.get("useToken"),
                    "created_at": format_date(attendance.get("createdAt")),
                    "updated_at": format_date(attendance.get("updatedAt")),
                    "timestamp": format_date(attendance.get("timestamp")),
                    "slc_edit": 0
                }

                # Check if record exists
                select_query = "SELECT * FROM attendance WHERE id = %s"
                existing_records = db.fetch_query(select_query, (attendance_id,))

                print(f"   [{i}/{len(created_attendances)}] Attendance ID {attendance_id}...")

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
                        UPDATE attendance SET
                            user_id = %s,
                            account_id = %s,
                            calander_id = %s,
                            session_id = %s,
                            group_session_id = %s,
                            is_present = %s,
                            day = %s,
                            note = %s,
                            is_editable = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s,
                            slc_edit = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["user_id"],
                        new_data["account_id"],
                        new_data["calander_id"],
                        new_data["session_id"],
                        new_data["group_session_id"],
                        new_data["is_present"],
                        new_data["day"],
                        new_data["note"],
                        new_data["is_editable"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        new_data["slc_edit"],
                        attendance_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO attendance (
                            id, user_id, account_id, calander_id, session_id, group_session_id,
                            is_present, day, note, is_editable, enabled,
                            releaseToken, useToken, created_at, updated_at, timestamp, slc_edit
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        attendance_id,
                        new_data["user_id"],
                        new_data["account_id"],
                        new_data["calander_id"],
                        new_data["session_id"],
                        new_data["group_session_id"],
                        new_data["is_present"],
                        new_data["day"],
                        new_data["note"],
                        new_data["is_editable"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        new_data["slc_edit"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing attendance ID {attendance.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_attendances: {err}")

    return result


def update_attendances(db, attendance_data):
    """
    Handle 'updated' attendances from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        attendance_data: Dictionary with 'updated' key

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
        updated_attendances = attendance_data.get("updated", [])
        result["total_processed"] = len(updated_attendances)

        if not updated_attendances:
            print("   ℹ️  No attendances in 'updated'")
            return result

        print(f"   Processing {len(updated_attendances)} attendance(s) from 'updated'...")

        for i, attendance in enumerate(updated_attendances, 1):
            try:
                attendance_id = attendance.get("id")
                if not attendance_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "user_id": attendance.get("userId"),
                    "account_id": attendance.get("accountId"),
                    "calander_id": attendance.get("calenderId"),
                    "session_id": attendance.get("sessionId"),
                    "group_session_id": attendance.get("groupId"),
                    "is_present": 1 if attendance.get("present", False) else 0,
                    "day": format_date(attendance.get("day")),
                    "note": attendance.get("note"),
                    "is_editable": 1 if attendance.get("editable", True) else 0,
                    "enabled": 1 if attendance.get("enabled", True) else 0,
                    "releaseToken": 1 if attendance.get("releaseToken", False) else 0,
                    "useToken": attendance.get("useToken"),
                    "updated_at": format_date(attendance.get("updatedAt")),
                    "timestamp": format_date(attendance.get("timestamp")),
                    "slc_edit": 1  # Mark as edited when updated
                }

                # Check if record exists
                select_query = "SELECT * FROM attendance WHERE id = %s"
                existing_records = db.fetch_query(select_query, (attendance_id,))

                print(f"   [{i}/{len(updated_attendances)}] Attendance ID {attendance_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
                    has_changes = False
                    for key, value in new_data.items():
                        # Skip slc_edit in comparison as it's always set to 1 in updates
                        if key == "slc_edit":
                            continue
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
                        UPDATE attendance SET
                            user_id = %s,
                            account_id = %s,
                            calander_id = %s,
                            session_id = %s,
                            group_session_id = %s,
                            is_present = %s,
                            day = %s,
                            note = %s,
                            is_editable = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            updated_at = %s,
                            timestamp = %s,
                            slc_edit = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["user_id"],
                        new_data["account_id"],
                        new_data["calander_id"],
                        new_data["session_id"],
                        new_data["group_session_id"],
                        new_data["is_present"],
                        new_data["day"],
                        new_data["note"],
                        new_data["is_editable"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        new_data["slc_edit"],
                        attendance_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO attendance (
                            id, user_id, account_id, calander_id, session_id, group_session_id,
                            is_present, day, note, is_editable, enabled,
                            releaseToken, useToken, created_at, updated_at, timestamp, slc_edit
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        attendance_id,
                        new_data["user_id"],
                        new_data["account_id"],
                        new_data["calander_id"],
                        new_data["session_id"],
                        new_data["group_session_id"],
                        new_data["is_present"],
                        new_data["day"],
                        new_data["note"],
                        new_data["is_editable"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"],
                        new_data["timestamp"],
                        new_data["slc_edit"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing attendance ID {attendance.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_attendances: {err}")

    return result


def process_attendances(db, attendance_data):
    """
    Process attendance data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        attendance_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING ATTENDANCES")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if attendance_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(attendance_data['created'])} records)...")
        results["created_section"] = insert_attendances(db, attendance_data)

    # Process 'updated' section
    if attendance_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(attendance_data['updated'])} records)...")
        results["updated_section"] = update_attendances(db, attendance_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 ATTENDANCES - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results