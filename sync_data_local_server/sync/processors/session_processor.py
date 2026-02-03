"""
Session Data Processor
Handles inserting and updating session records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_sessions(db, session_data):
    """
    Handle 'created' sessions from API
    Logic:
    - If session exists in DB → UPDATE it
    - If session does NOT exist → INSERT it

    Args:
        db: Database instance
        session_data: Dictionary with 'created' key

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
        created_sessions = session_data.get("created", [])
        result["total_processed"] = len(created_sessions)

        if not created_sessions:
            print("   ℹ️  No sessions in 'created'")
            return result

        print(f"   Processing {len(created_sessions)} session(s) from 'created'...")

        for i, session in enumerate(created_sessions, 1):
            try:
                session_id = session.get("id")
                if not session_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data with safe defaults
                new_data = {
                    "uuid": session.get("uuid"),
                    "account_id": session.get("accountId"),
                    "formation_id": session.get("formationId"),
                    "name": session.get("name", ""),
                    "description": session.get("description"),
                    "status": 1 if session.get("status", True) else 0,
                    "img_link": session.get("image"),
                    "start_date": format_date(session.get("startDate")),
                    "end_date": format_date(session.get("endDate")),
                    "capacity": session.get("capacity", 0),
                    "price": session.get("price", 0),
                    "currency": session.get("currency"),
                    "type_pay": session.get("typePay"),
                    "request_change_group": 1 if session.get("requestChangeGroup", False) else 0,
                    "max_group_change": session.get("maxGroupChange", 0),
                    "special_group": 1 if session.get("specialGroup", False) else 0,
                    "enabled": 1 if session.get("enabled", True) else 0,
                    "user_register_after_start": 1,
                    "releaseToken": 1 if session.get("releaseToken", False) else 0,
                    "useToken": session.get("useToken"),
                    "created_at": format_date(session.get("createdAt")),
                    "updated_at": format_date(session.get("updatedAt")),
                    "timestamp": format_date(session.get("timestamp")),
                    "payment_methode": None,
                    "number_session_for_pay": None,
                    "price_student_absent": None,
                    "public_resource": None,
                    "price_presence": None,
                    "price_online": None,
                    "passage": None,
                    "season_id": None
                }

                # Check if session exists
                select_query = "SELECT * FROM session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (session_id,))

                print(f"   [{i}/{len(created_sessions)}] Session ID {session_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
                    has_changes = False
                    for key, value in new_data.items():
                        if key in ["payment_methode", "number_session_for_pay", "price_student_absent",
                                   "public_resource", "price_presence", "price_online", "passage", "season_id"]:
                            # Skip comparison for fields that are always None in new_data
                            continue

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
                        UPDATE session SET
                            uuid = %s,
                            account_id = %s,
                            formation_id = %s,
                            name = %s,
                            description = %s,
                            status = %s,
                            img_link = %s,
                            start_date = %s,
                            end_date = %s,
                            capacity = %s,
                            price = %s,
                            currency = %s,
                            type_pay = %s,
                            request_change_group = %s,
                            max_group_change = %s,
                            special_group = %s,
                            enabled = %s,
                            user_register_after_start = %s,
                            releaseToken = %s,
                            useToken = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s,
                            payment_methode = %s,
                            number_session_for_pay = %s,
                            price_student_absent = %s,
                            public_resource = %s,
                            price_presence = %s,
                            price_online = %s,
                            passage = %s,
                            season_id = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["uuid"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["img_link"],
                        new_data["start_date"],
                        new_data["end_date"],
                        new_data["capacity"],
                        new_data["price"],
                        new_data["currency"],
                        new_data["type_pay"],
                        new_data["request_change_group"],
                        new_data["max_group_change"],
                        new_data["special_group"],
                        new_data["enabled"],
                        new_data["user_register_after_start"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        new_data["payment_methode"],
                        new_data["number_session_for_pay"],
                        new_data["price_student_absent"],
                        new_data["public_resource"],
                        new_data["price_presence"],
                        new_data["price_online"],
                        new_data["passage"],
                        new_data["season_id"],
                        session_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New session - inserting...")

                    insert_query = """
                        INSERT INTO session (
                            id, uuid, account_id, formation_id, name, description, status, img_link,
                            start_date, end_date, capacity, price, currency, type_pay,
                            request_change_group, max_group_change, special_group, enabled, 
                            user_register_after_start, releaseToken, useToken, created_at, 
                            updated_at, timestamp, payment_methode, number_session_for_pay, 
                            price_student_absent, public_resource, price_presence, price_online, 
                            passage, season_id
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        session_id,
                        new_data["uuid"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["img_link"],
                        new_data["start_date"],
                        new_data["end_date"],
                        new_data["capacity"],
                        new_data["price"],
                        new_data["currency"],
                        new_data["type_pay"],
                        new_data["request_change_group"],
                        new_data["max_group_change"],
                        new_data["special_group"],
                        new_data["enabled"],
                        new_data["user_register_after_start"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        new_data["payment_methode"],
                        new_data["number_session_for_pay"],
                        new_data["price_student_absent"],
                        new_data["public_resource"],
                        new_data["price_presence"],
                        new_data["price_online"],
                        new_data["passage"],
                        new_data["season_id"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing session ID {session.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_sessions: {err}")

    return result


def update_sessions(db, session_data):
    """
    Handle 'updated' sessions from API
    Logic:
    - If session exists in DB → UPDATE it
    - If session does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        session_data: Dictionary with 'updated' key

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
        updated_sessions = session_data.get("updated", [])
        result["total_processed"] = len(updated_sessions)

        if not updated_sessions:
            print("   ℹ️  No sessions in 'updated'")
            return result

        print(f"   Processing {len(updated_sessions)} session(s) from 'updated'...")

        for i, session in enumerate(updated_sessions, 1):
            try:
                session_id = session.get("id")
                if not session_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "uuid": session.get("uuid"),
                    "account_id": session.get("accountId"),
                    "formation_id": session.get("formationId"),
                    "name": session.get("name"),
                    "description": session.get("description"),
                    "status": 1 if session.get("status", True) else 0,
                    "img_link": session.get("image"),
                    "start_date": format_date(session.get("startDate")),
                    "end_date": format_date(session.get("endDate")),
                    "capacity": session.get("capacity", 0),
                    "price": session.get("price", 0),
                    "currency": session.get("currency"),
                    "type_pay": session.get("typePay"),
                    "request_change_group": 1 if session.get("requestChangeGroup", False) else 0,
                    "max_group_change": session.get("maxGroupChange", 0),
                    "special_group": 1 if session.get("specialGroup", False) else 0,
                    "enabled": 1 if session.get("enabled", True) else 0,
                    "user_register_after_start": 1,
                    "releaseToken": 1 if session.get("releaseToken", False) else 0,
                    "useToken": session.get("useToken"),
                    "updated_at": format_date(session.get("updatedAt")),
                    "timestamp": format_date(session.get("timestamp"))
                }

                # Check if session exists
                select_query = "SELECT * FROM session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (session_id,))

                print(f"   [{i}/{len(updated_sessions)}] Session ID {session_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data (skip fields that are always None or not in new_data)
                    has_changes = False
                    # Compare only relevant fields
                    comparison_fields = ["uuid", "account_id", "formation_id", "name", "description",
                                         "status", "img_link", "start_date", "end_date", "capacity",
                                         "price", "currency", "type_pay", "request_change_group",
                                         "max_group_change", "special_group", "enabled",
                                         "user_register_after_start", "releaseToken", "useToken",
                                         "created_at", "updated_at", "timestamp"]

                    has_changes = False
                    for field in comparison_fields:
                        old_value = str(existing.get(field)) if existing.get(field) is not None else None
                        new_value = str(new_data.get(field)) if new_data.get(field) is not None else None
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
                        UPDATE session SET
                            uuid = %s,
                            account_id = %s,
                            formation_id = %s,
                            name = %s,
                            description = %s,
                            status = %s,
                            img_link = %s,
                            start_date = %s,
                            end_date = %s,
                            capacity = %s,
                            price = %s,
                            currency = %s,
                            type_pay = %s,
                            request_change_group = %s,
                            max_group_change = %s,
                            special_group = %s,
                            enabled = %s,
                            user_register_after_start = %s,
                            releaseToken = %s,
                            useToken = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["uuid"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["img_link"],
                        new_data["start_date"],
                        new_data["end_date"],
                        new_data["capacity"],
                        new_data["price"],
                        new_data["currency"],
                        new_data["type_pay"],
                        new_data["request_change_group"],
                        new_data["max_group_change"],
                        new_data["special_group"],
                        new_data["enabled"],
                        new_data["user_register_after_start"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        session_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Session not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO session (
                            id, uuid, account_id, formation_id, name, description, status, img_link,
                            start_date, end_date, capacity, price, currency, type_pay,
                            request_change_group, max_group_change, special_group, enabled, 
                            user_register_after_start, releaseToken, useToken, created_at, 
                            updated_at, timestamp, payment_methode, number_session_for_pay, 
                            price_student_absent, public_resource, price_presence, price_online, 
                            passage, season_id
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    # Set NULL values for optional fields
                    db.execute_query(insert_query, (
                        session_id,
                        new_data["uuid"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["status"],
                        new_data["img_link"],
                        new_data["start_date"],
                        new_data["end_date"],
                        new_data["capacity"],
                        new_data["price"],
                        new_data["currency"],
                        new_data["type_pay"],
                        new_data["request_change_group"],
                        new_data["max_group_change"],
                        new_data["special_group"],
                        new_data["enabled"],
                        new_data["user_register_after_start"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"],
                        new_data["timestamp"],
                        None,  # payment_methode
                        None,  # number_session_for_pay
                        None,  # price_student_absent
                        None,  # public_resource
                        None,  # price_presence
                        None,  # price_online
                        None,  # passage
                        None  # season_id
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing session ID {session.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_sessions: {err}")

    return result


def process_sessions(db, session_data):
    """
    Process session data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        session_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING SESSIONS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if session_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(session_data['created'])} records)...")
        results["created_section"] = insert_sessions(db, session_data)

    # Process 'updated' section
    if session_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(session_data['updated'])} records)...")
        results["updated_section"] = update_sessions(db, session_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 SESSIONS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results