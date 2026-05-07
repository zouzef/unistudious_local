"""
Payment Session Data Processor
Handles inserting and updating payment_session records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_payment_sessions(db, payment_data):
    """
    Handle 'created' payment sessions from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        payment_data: Dictionary with 'created' key

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
        created_payments = payment_data.get("created", [])
        result["total_processed"] = len(created_payments)

        if not created_payments:
            print("   ℹ️  No payment sessions in 'created'")
            return result

        print(f"   Processing {len(created_payments)} payment session(s) from 'created'...")

        for i, payment in enumerate(created_payments, 1):
            try:
                payment_id = payment.get("id")
                if not payment_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "uuid": payment.get("uuid", ""),
                    "session_id": payment.get("sessionId"),
                    "account_id": payment.get("accountId"),
                    "user_id": payment.get("userId"),
                    "type": payment.get("type", ""),
                    "type_date": payment.get("type_Date"),
                    "type_number_session": payment.get("type_number_session"),
                    "date_payment": format_date(payment.get("date_payment")),
                    "status": payment.get("status", "Pending"),
                    "amount": payment.get("amount"),
                    "created_by": payment.get("created_by"),
                    "price": payment.get("price"),
                    "description": payment.get("description"),
                    "forcing": payment.get("forcing"),
                    "enabled": 1 if payment.get("enabled") else 0,
                    "created_at": format_date(payment.get("createdAt")),
                    "updated_at": format_date(payment.get("updatedAt")),
                    "timestamp": format_date(payment.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM payment_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (payment_id,))

                print(f"   [{i}/{len(created_payments)}] Payment Session ID {payment_id}...")

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
                        UPDATE payment_session SET
                            uuid = %s,
                            session_id = %s,
                            account_id = %s,
                            user_id = %s,
                            type = %s,
                            type_date = %s,
                            type_number_session = %s,
                            date_payment = %s,
                            status = %s,
                            amount = %s,
                            created_by = %s,
                            price = %s,
                            description = %s,
                            forcing = %s,
                            enabled = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["uuid"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["type"],
                        new_data["type_date"],
                        new_data["type_number_session"],
                        new_data["date_payment"],
                        new_data["status"],
                        new_data["amount"],
                        new_data["created_by"],
                        new_data["price"],
                        new_data["description"],
                        new_data["forcing"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        payment_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO payment_session (
                            id, uuid, session_id, account_id, user_id, type, type_date,
                            type_number_session, date_payment, status, amount, created_by,
                            price, description, forcing, enabled, created_at, updated_at, timestamp
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        payment_id,
                        new_data["uuid"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["type"],
                        new_data["type_date"],
                        new_data["type_number_session"],
                        new_data["date_payment"],
                        new_data["status"],
                        new_data["amount"],
                        new_data["created_by"],
                        new_data["price"],
                        new_data["description"],
                        new_data["forcing"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing payment session ID {payment.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_payment_sessions: {err}")

    return result


def update_payment_sessions(db, payment_data):
    """
    Handle 'updated' payment sessions from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        payment_data: Dictionary with 'updated' key

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
        updated_payments = payment_data.get("updated", [])
        result["total_processed"] = len(updated_payments)

        if not updated_payments:
            print("   ℹ️  No payment sessions in 'updated'")
            return result

        print(f"   Processing {len(updated_payments)} payment session(s) from 'updated'...")

        for i, payment in enumerate(updated_payments, 1):
            try:
                payment_id = payment.get("id")
                if not payment_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "uuid": payment.get("uuid", ""),
                    "session_id": payment.get("sessionId"),
                    "account_id": payment.get("accountId"),
                    "user_id": payment.get("userId"),
                    "type": payment.get("type", ""),
                    "type_date": payment.get("type_Date"),
                    "type_number_session": payment.get("type_number_session"),
                    "date_payment": format_date(payment.get("date_payment")),
                    "status": payment.get("status", "Pending"),
                    "amount": payment.get("amount"),
                    "created_by": payment.get("created_by"),
                    "price": payment.get("price"),
                    "description": payment.get("description"),
                    "forcing": payment.get("forcing"),
                    "enabled": 1 if payment.get("enabled") else 0,
                    "created_at": format_date(payment.get("createdAt")),
                    "updated_at": format_date(payment.get("updatedAt")),
                    "timestamp": format_date(payment.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM payment_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (payment_id,))

                print(f"   [{i}/{len(updated_payments)}] Payment Session ID {payment_id}...")

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
                        UPDATE payment_session SET
                            uuid = %s,
                            session_id = %s,
                            account_id = %s,
                            user_id = %s,
                            type = %s,
                            type_date = %s,
                            type_number_session = %s,
                            date_payment = %s,
                            status = %s,
                            amount = %s,
                            created_by = %s,
                            price = %s,
                            description = %s,
                            forcing = %s,
                            enabled = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["uuid"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["type"],
                        new_data["type_date"],
                        new_data["type_number_session"],
                        new_data["date_payment"],
                        new_data["status"],
                        new_data["amount"],
                        new_data["created_by"],
                        new_data["price"],
                        new_data["description"],
                        new_data["forcing"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        payment_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO payment_session (
                            id, uuid, session_id, account_id, user_id, type, type_date,
                            type_number_session, date_payment, status, amount, created_by,
                            price, description, forcing, enabled, created_at, updated_at, timestamp
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        payment_id,
                        new_data["uuid"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["type"],
                        new_data["type_date"],
                        new_data["type_number_session"],
                        new_data["date_payment"],
                        new_data["status"],
                        new_data["amount"],
                        new_data["created_by"],
                        new_data["price"],
                        new_data["description"],
                        new_data["forcing"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing payment session ID {payment.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_payment_sessions: {err}")

    return result


def process_payment_sessions(db, payment_data):
    """
    Process payment session data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        payment_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING PAYMENT SESSIONS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if payment_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(payment_data['created'])} records)...")
        results["created_section"] = insert_payment_sessions(db, payment_data)

    # Process 'updated' section
    if payment_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(payment_data['updated'])} records)...")
        results["updated_section"] = update_payment_sessions(db, payment_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 PAYMENT SESSIONS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results