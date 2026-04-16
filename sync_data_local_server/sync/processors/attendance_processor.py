"""
Attendance Data Processor
Handles inserting and updating attendance records in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date, get_mac_address, reset_attendance_token, get_all_calendar_ids, get_all_group_ids


def insert_attendances(db, attendance_data, settings):
    result = {"inserted": 0, "skipped": 0, "errors": 0, "total_processed": 0}

    try:
        created_attendances = attendance_data.get("created", [])
        result["total_processed"] = len(created_attendances)

        if not created_attendances:
            print("   ℹ️  No attendances in 'created'")
            return result

        local_mac = get_mac_address(db)
        calendar_mapping = get_all_calendar_ids(db)
        group_mapping = get_all_group_ids(db)  # ✅ fix 1 — was wrong position and wrong syntax
        print(f"   🖥️  Local MAC: {local_mac}")
        print(f"   Processing {len(created_attendances)} attendance(s) from 'created'...")

        for i, attendance in enumerate(created_attendances, 1):
            try:
                attendance_id = attendance.get("id")
                if not attendance_id:
                    raise ValueError("Missing required field: id")

                print(f"   [{i}/{len(created_attendances)}] Attendance ID {attendance_id}...")

                existing = db.fetch_query(
                    "SELECT id FROM attendance WHERE id_prod = %s", (attendance_id,)
                )

                if existing:
                    remote_mac = attendance.get("useToken")
                    if local_mac and remote_mac and remote_mac == local_mac:
                        print(f"      ⏭️  Skipping — originated from this server (MAC match)")
                        reset_attendance_token(settings, attendance_id)
                        result["skipped"] += 1
                        continue

                    print(f"      ⏭️  Already exists (id_prod={attendance_id}) — skipping")
                    result["skipped"] += 1
                    continue

                # ✅ NOT EXISTS → INSERT
                print(f"      ✨ New record — inserting...")

                # ✅ Convert remote calenderId to local id
                local_calendar_id = calendar_mapping.get(attendance.get("calenderId"))
                if not local_calendar_id:
                    print(f"      ❌ No local calendar found for remote id={attendance.get('calenderId')} — skipping")
                    result["errors"] += 1
                    continue

                # ✅ fix 2 — convert remote groupId to local id inside the loop
                local_group_id = group_mapping.get(attendance.get("groupId"))
                if not local_group_id:
                    print(f"      ❌ No local group found for remote id={attendance.get('groupId')} — skipping")
                    result["errors"] += 1
                    continue

                insert_query = """
                    INSERT INTO attendance (
                        id, user_id, account_id, calander_id, session_id, group_session_id,
                        is_present, day, note, is_editable, enabled,
                        releaseToken, useToken, created_at, updated_at, timestamp, slc_edit, id_prod
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                db.execute_query(insert_query, (
                    attendance_id,
                    attendance.get("userId"),
                    attendance.get("accountId"),
                    local_calendar_id,  # ✅ local calendar id
                    attendance.get("sessionId"),
                    local_group_id,     # ✅ local group id
                    1 if attendance.get("present", False) else 0,
                    format_date(attendance.get("day")),
                    attendance.get("note"),
                    1 if attendance.get("editable", True) else 0,
                    1 if attendance.get("enabled", True) else 0,
                    1 if attendance.get("releaseToken", False) else 0,
                    attendance.get("useToken"),
                    format_date(attendance.get("createdAt")),
                    format_date(attendance.get("updatedAt")),
                    format_date(attendance.get("timestamp")),
                    0,
                    attendance_id
                ))

                result["inserted"] += 1
                print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing attendance ID {attendance.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created → Inserted: {result['inserted']}, "
              f"Skipped: {result['skipped']}, Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_attendances: {err}")

    return result


def update_attendances(db, attendance_data, settings):
    result = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0, "total_processed": 0}

    try:
        updated_attendances = attendance_data.get("updated", [])
        result["total_processed"] = len(updated_attendances)

        if not updated_attendances:
            print("   ℹ️  No attendances in 'updated'")
            return result

        local_mac = get_mac_address(db)
        calendar_mapping = get_all_calendar_ids(db)
        group_mapping = get_all_group_ids(db)  # ✅ fix 3 — was missing
        print(f"   🖥️  Local MAC: {local_mac}")
        print(f"   Processing {len(updated_attendances)} attendance(s) from 'updated'...")

        for i, attendance in enumerate(updated_attendances, 1):
            try:
                attendance_id = attendance.get("id")
                if not attendance_id:
                    raise ValueError("Missing required field: id")

                print(f"   [{i}/{len(updated_attendances)}] Attendance ID {attendance_id}...")

                existing_by_prod = db.fetch_query(
                    "SELECT id FROM attendance WHERE id_prod = %s", (attendance_id,)
                )

                if existing_by_prod:
                    local_id = existing_by_prod[0]['id']

                    remote_mac = attendance.get("useToken")
                    print(f"      🔍 local_mac={local_mac} | remote_mac={remote_mac}")

                    if local_mac and remote_mac and remote_mac == local_mac:
                        print(f"      ⏭️  Skipping — originated from this server (MAC match)")
                        reset_attendance_token(settings, attendance_id)
                        result["skipped"] += 1
                        continue

                    new_data = {
                        "user_id": attendance.get("userId"),
                        "account_id": attendance.get("accountId"),
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
                    }

                    existing_full = db.fetch_query(
                        "SELECT * FROM attendance WHERE id = %s", (local_id,)
                    )[0]

                    has_changes = False
                    for key, value in new_data.items():
                        old_value = str(existing_full.get(key)) if existing_full.get(key) is not None else None
                        new_value = str(value) if value is not None else None
                        if old_value != new_value:
                            has_changes = True
                            break

                    if not has_changes:
                        print(f"      ⏭️  Data identical — skipped")
                        result["skipped"] += 1
                        continue

                    print(f"      🔄 Data changed — updating...")

                    update_query = """
                        UPDATE attendance SET
                            user_id = %s,
                            account_id = %s,
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
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["user_id"],
                        new_data["account_id"],
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
                        local_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")
                    continue

                # ✅ NOT EXISTS → INSERT
                print(f"      ⚠️  Not found — inserting...")

                # ✅ Convert remote calenderId to local id
                local_calendar_id = calendar_mapping.get(attendance.get("calenderId"))
                if not local_calendar_id:
                    print(f"      ❌ No local calendar found for remote id={attendance.get('calenderId')} — skipping")
                    result["errors"] += 1
                    continue

                # ✅ fix 4 — convert remote groupId to local id inside the loop
                local_group_id = group_mapping.get(attendance.get("groupId"))
                if not local_group_id:
                    print(f"      ❌ No local group found for remote id={attendance.get('groupId')} — skipping")
                    result["errors"] += 1
                    continue

                insert_query = """
                    INSERT INTO attendance (
                        id, user_id, account_id, calander_id, session_id, group_session_id,
                        is_present, day, note, is_editable, enabled,
                        releaseToken, useToken, created_at, updated_at, timestamp, slc_edit, id_prod
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                db.execute_query(insert_query, (
                    attendance_id,
                    attendance.get("userId"),
                    attendance.get("accountId"),
                    local_calendar_id,  # ✅ local calendar id
                    attendance.get("sessionId"),
                    local_group_id,     # ✅ local group id
                    1 if attendance.get("present", False) else 0,
                    format_date(attendance.get("day")),
                    attendance.get("note"),
                    1 if attendance.get("editable", True) else 0,
                    1 if attendance.get("enabled", True) else 0,
                    1 if attendance.get("releaseToken", False) else 0,
                    attendance.get("useToken"),
                    format_date(attendance.get("updatedAt")),
                    format_date(attendance.get("updatedAt")),
                    format_date(attendance.get("timestamp")),
                    0,
                    attendance_id
                ))

                result["inserted"] += 1
                print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing attendance ID {attendance.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_attendances: {err}")

    return result


def process_attendances(db, attendance_data, settings):
    print("\n📌 PROCESSING ATTENDANCES")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if attendance_data.get("created"):
        print(f"\n✨ Processing 'created' ({len(attendance_data['created'])} records)...")
        results["created_section"] = insert_attendances(db, attendance_data, settings)

    if attendance_data.get("updated"):
        print(f"\n🔄 Processing 'updated' ({len(attendance_data['updated'])} records)...")
        results["updated_section"] = update_attendances(db, attendance_data, settings)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["updated_section"].get("updated", 0)
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