"""
Calendar Data Processor
Handles inserting and updating calendar records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date
from datetime import datetime


def insert_attendance_calendar(db, calendar_id, session_id, group_session_id, account_id, day):
    """
    Insert attendance records for all users in a session when a calendar entry is created

    Args:
        db: Database instance
        calendar_id: Calendar ID
        session_id: Session ID
        group_session_id: Group session ID
        account_id: Account ID
        day: Date of the calendar entry
    """
    try:
        print("      📝 Adding attendance records for calendar...")

        # Check if attendance already added for this calendar
        check_query = "SELECT * FROM attendance WHERE calander_id = %s"
        existing_attendance = db.fetch_query(check_query, (calendar_id,))

        if existing_attendance:
            print("      ℹ️  Attendance already exists for this calendar - skipping")
            return

        # Get users for this session and group
        user_query = """
            SELECT user_id FROM relation_user_session 
            WHERE session_id = %s AND relation_group_local_session_id = %s AND enabled = 1
        """
        users = db.fetch_query(user_query, (session_id, group_session_id))

        if not users:
            print("      ℹ️  No users found for this session")
            return

        user_list = [row["user_id"] for row in users]

        # Get max ID to generate new IDs
        max_id_query = "SELECT MAX(id) as max_id FROM attendance"
        max_id_result = db.fetch_query(max_id_query)
        max_id = max_id_result[0]["max_id"] if max_id_result and max_id_result[0]["max_id"] else 0

        # Current system datetime
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert attendance for each user
        insert_query = """
            INSERT INTO attendance (
                id, user_id, session_id, account_id, group_session_id, calander_id,
                payment_session_id, is_present, day, note, is_editable, enabled,
                created_at, timestamp, updated_at, releaseToken, useToken, is_sync, slc_edit
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for i, user_id in enumerate(user_list, 1):
            new_id = max_id + i
            db.execute_query(insert_query, (
                new_id, user_id, session_id, account_id, group_session_id, calendar_id,
                None, 0, day, None, 1, 1, created_at, created_at, None, 0, None, 0, 0
            ))
            print(f"      ✅ Attendance inserted for user {user_id}")

        print(f"      📊 Total attendance records created: {len(user_list)}")

    except Exception as ex:
        print(f"      ❌ Error creating attendance records: {ex}")


def insert_calendars(db, calendar_data):
    """
    Handle 'created' calendars from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        calendar_data: Dictionary with 'created' key

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
        created_calendars = calendar_data.get("created", [])
        result["total_processed"] = len(created_calendars)

        if not created_calendars:
            print("   ℹ️  No calendars in 'created'")
            return result

        print(f"   Processing {len(created_calendars)} calendar(s) from 'created'...")

        for i, calendar in enumerate(created_calendars, 1):
            try:
                calendar_id = calendar.get("id")
                if not calendar_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "session_id": calendar.get("sessionId"),
                    "account_id": calendar.get("accountId"),
                    "local_id": calendar.get("localId"),
                    "group_session_id": calendar.get("groupId"),
                    "room_id": calendar.get("roomId"),
                    "teacher_id": calendar.get("teacherId"),
                    "subject_id": calendar.get("subjectId"),
                    "color": calendar.get("color"),
                    "status": 1 if calendar.get("status", True) else 0,
                    "description": calendar.get("description"),
                    "start_time": format_date(calendar.get("start_time")),
                    "end_time": format_date(calendar.get("end_time")),
                    "ref": calendar.get("ref"),
                    "date": format_date(calendar.get("date")),
                    "refresh": 1 if calendar.get("refresh", False) else 0,
                    "title": calendar.get("title", ""),
                    "enabled": 1 if calendar.get("enabled", True) else 0,
                    "type": calendar.get("type"),
                    "teacher_present": 1 if calendar.get("teacher_present", False) else 0,
                    "force_teacher_present": 1 if calendar.get("force_teacher_present", False) else 0,
                    "releaseToken": 1 if calendar.get("releaseToken", False) else 0,
                    "useToken": calendar.get("useToken"),
                    "created_at": format_date(calendar.get("createdAt")),
                    "updated_at": format_date(calendar.get("updatedAt")),
                    "timestamp": format_date(calendar.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM relation_calander_group_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (calendar_id,))

                print(f"   [{i}/{len(created_calendars)}] Calendar ID {calendar_id}...")

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
                        UPDATE relation_calander_group_session SET
                            session_id = %s,
                            account_id = %s,
                            local_id = %s,
                            group_session_id = %s,
                            room_id = %s,
                            teacher_id = %s,
                            subject_id = %s,
                            color = %s,
                            status = %s,
                            description = %s,
                            start_time = %s,
                            end_time = %s,
                            ref = %s,
                            date = %s,
                            refresh = %s,
                            title = %s,
                            enabled = %s,
                            type = %s,
                            teacher_present = %s,
                            force_teacher_present = %s,
                            releaseToken = %s,
                            useToken = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["local_id"],
                        new_data["group_session_id"],
                        new_data["room_id"],
                        new_data["teacher_id"],
                        new_data["subject_id"],
                        new_data["color"],
                        new_data["status"],
                        new_data["description"],
                        new_data["start_time"],
                        new_data["end_time"],
                        new_data["ref"],
                        new_data["date"],
                        new_data["refresh"],
                        new_data["title"],
                        new_data["enabled"],
                        new_data["type"],
                        new_data["teacher_present"],
                        new_data["force_teacher_present"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        calendar_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO relation_calander_group_session (
                            id, session_id, account_id, local_id, group_session_id, room_id,
                            teacher_id, subject_id, color, status, description, start_time,
                            end_time, ref, date, refresh, title, enabled, type,
                            teacher_present, force_teacher_present, releaseToken, useToken,
                            created_at, updated_at, timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        calendar_id,
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["local_id"],
                        new_data["group_session_id"],
                        new_data["room_id"],
                        new_data["teacher_id"],
                        new_data["subject_id"],
                        new_data["color"],
                        new_data["status"],
                        new_data["description"],
                        new_data["start_time"],
                        new_data["end_time"],
                        new_data["ref"],
                        new_data["date"],
                        new_data["refresh"],
                        new_data["title"],
                        new_data["enabled"],
                        new_data["type"],
                        new_data["teacher_present"],
                        new_data["force_teacher_present"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

                    # Optional: Create attendance records for this calendar
                    # Uncomment the lines below if you want to auto-create attendance
                    # if new_data["session_id"] and new_data["group_session_id"] and new_data["account_id"] and new_data["date"]:
                    #     insert_attendance_calendar(
                    #         db, calendar_id, new_data["session_id"],
                    #         new_data["group_session_id"], new_data["account_id"], new_data["date"]
                    #     )

            except Exception as err:
                print(f"      ❌ Error processing calendar ID {calendar.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_calendars: {err}")

    return result


def update_calendars(db, calendar_data):
    """
    Handle 'updated' calendars from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        calendar_data: Dictionary with 'updated' key

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
        updated_calendars = calendar_data.get("updated", [])
        result["total_processed"] = len(updated_calendars)

        if not updated_calendars:
            print("   ℹ️  No calendars in 'updated'")
            return result

        print(f"   Processing {len(updated_calendars)} calendar(s) from 'updated'...")

        for i, calendar in enumerate(updated_calendars, 1):
            try:
                calendar_id = calendar.get("id")
                if not calendar_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "session_id": calendar.get("sessionId"),
                    "account_id": calendar.get("accountId"),
                    "local_id": calendar.get("localId"),
                    "group_session_id": calendar.get("groupId"),
                    "room_id": calendar.get("roomId"),
                    "teacher_id": calendar.get("teacherId"),
                    "subject_id": calendar.get("subjectId"),
                    "color": calendar.get("color"),
                    "status": 1 if calendar.get("status", True) else 0,
                    "description": calendar.get("description"),
                    "start_time": format_date(calendar.get("start_time")),
                    "end_time": format_date(calendar.get("end_time")),
                    "ref": calendar.get("ref"),
                    "date": format_date(calendar.get("date")),
                    "refresh": 1 if calendar.get("refresh", False) else 0,
                    "title": calendar.get("title", ""),
                    "enabled": 1 if calendar.get("enabled", True) else 0,
                    "type": calendar.get("type"),
                    "teacher_present": 1 if calendar.get("teacher_present", False) else 0,
                    "force_teacher_present": 1 if calendar.get("force_teacher_present", False) else 0,
                    "releaseToken": 1 if calendar.get("releaseToken", False) else 0,
                    "useToken": calendar.get("useToken"),
                    "updated_at": format_date(calendar.get("updatedAt")),
                    "timestamp": format_date(calendar.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM relation_calander_group_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (calendar_id,))

                print(f"   [{i}/{len(updated_calendars)}] Calendar ID {calendar_id}...")

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
                        UPDATE relation_calander_group_session SET
                            session_id = %s,
                            account_id = %s,
                            local_id = %s,
                            group_session_id = %s,
                            room_id = %s,
                            teacher_id = %s,
                            subject_id = %s,
                            color = %s,
                            status = %s,
                            description = %s,
                            start_time = %s,
                            end_time = %s,
                            ref = %s,
                            date = %s,
                            refresh = %s,
                            title = %s,
                            enabled = %s,
                            type = %s,
                            teacher_present = %s,
                            force_teacher_present = %s,
                            releaseToken = %s,
                            useToken = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["local_id"],
                        new_data["group_session_id"],
                        new_data["room_id"],
                        new_data["teacher_id"],
                        new_data["subject_id"],
                        new_data["color"],
                        new_data["status"],
                        new_data["description"],
                        new_data["start_time"],
                        new_data["end_time"],
                        new_data["ref"],
                        new_data["date"],
                        new_data["refresh"],
                        new_data["title"],
                        new_data["enabled"],
                        new_data["type"],
                        new_data["teacher_present"],
                        new_data["force_teacher_present"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        calendar_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO relation_calander_group_session (
                            id, session_id, account_id, local_id, group_session_id, room_id,
                            teacher_id, subject_id, color, status, description, start_time,
                            end_time, ref, date, refresh, title, enabled, type,
                            teacher_present, force_teacher_present, releaseToken, useToken,
                            created_at, updated_at, timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        calendar_id,
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["local_id"],
                        new_data["group_session_id"],
                        new_data["room_id"],
                        new_data["teacher_id"],
                        new_data["subject_id"],
                        new_data["color"],
                        new_data["status"],
                        new_data["description"],
                        new_data["start_time"],
                        new_data["end_time"],
                        new_data["ref"],
                        new_data["date"],
                        new_data["refresh"],
                        new_data["title"],
                        new_data["enabled"],
                        new_data["type"],
                        new_data["teacher_present"],
                        new_data["force_teacher_present"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing calendar ID {calendar.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_calendars: {err}")

    return result


def process_calendars(db, calendar_data):
    """
    Process calendar data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        calendar_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING CALENDARS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if calendar_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(calendar_data['created'])} records)...")
        results["created_section"] = insert_calendars(db, calendar_data)

    # Process 'updated' section
    if calendar_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(calendar_data['updated'])} records)...")
        results["updated_section"] = update_calendars(db, calendar_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 CALENDARS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results