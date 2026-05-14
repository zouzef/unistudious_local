"""
Invoice Data Processor
Handles inserting and updating invoice records in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_invoice(db, invoice_data):
    """
    Handle 'created' invoice records from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        invoice_data: Dictionary with 'created' key

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
        created_records = invoice_data.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No invoice records in 'created'")
            return result

        print(f"   Processing {len(created_records)} invoice record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data — map API fields → DB columns
                new_data = {
                    "account_id":        record.get("accountId"),
                    "user_id":           record.get("userId"),
                    "session_id":        record.get("sessionId"),
                    "payment_session_id":record.get("PaymentId"),
                    "name":              record.get("name"),
                    "type":              record.get("type"),
                    "file_link":         record.get("FileLink"),
                    "description":       record.get("description"),
                    "is_status":         1 if record.get("status") else 0,
                    "created_by":        record.get("created_by"),
                    "total_amount":      record.get("totalAmount"),
                    "enabled":           1 if record.get("enabled") else 0,
                    "timestamp":         format_date(record.get("timestamp")),
                    "created_at":        format_date(record.get("createdAt")),
                    "updated_at":        format_date(record.get("updatedAt")),
                }

                # Check if record exists
                select_query = "SELECT * FROM invoice WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] Invoice ID {record_id}...")

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
                        UPDATE invoice SET
                            account_id         = %s,
                            user_id            = %s,
                            session_id         = %s,
                            payment_session_id = %s,
                            name               = %s,
                            type               = %s,
                            file_link          = %s,
                            description        = %s,
                            is_status          = %s,
                            created_by         = %s,
                            total_amount       = %s,
                            enabled            = %s,
                            timestamp          = %s,
                            created_at         = %s,
                            updated_at         = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["payment_session_id"],
                        new_data["name"],
                        new_data["type"],
                        new_data["file_link"],
                        new_data["description"],
                        new_data["is_status"],
                        new_data["created_by"],
                        new_data["total_amount"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO invoice (
                            id, account_id, user_id, session_id, payment_session_id,
                            name, type, file_link, description, is_status,
                            created_by, total_amount, enabled,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["payment_session_id"],
                        new_data["name"],
                        new_data["type"],
                        new_data["file_link"],
                        new_data["description"],
                        new_data["is_status"],
                        new_data["created_by"],
                        new_data["total_amount"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing invoice ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_invoice: {err}")

    return result


def update_invoice(db, invoice_data):
    """
    Handle 'updated' invoice records from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        invoice_data: Dictionary with 'updated' key

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
        updated_records = invoice_data.get("updated", [])
        result["total_processed"] = len(updated_records)

        if not updated_records:
            print("   ℹ️  No invoice records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} invoice record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data — map API fields → DB columns
                new_data = {
                    "account_id":        record.get("accountId"),
                    "user_id":           record.get("userId"),
                    "session_id":        record.get("sessionId"),
                    "payment_session_id":record.get("PaymentId"),
                    "name":              record.get("name"),
                    "type":              record.get("type"),
                    "file_link":         record.get("FileLink"),
                    "description":       record.get("description"),
                    "is_status":         1 if record.get("status") else 0,
                    "created_by":        record.get("created_by"),
                    "total_amount":      record.get("totalAmount"),
                    "enabled":           1 if record.get("enabled") else 0,
                    "timestamp":         format_date(record.get("timestamp")),
                    "updated_at":        format_date(record.get("updatedAt")),
                }

                # Check if record exists
                select_query = "SELECT * FROM invoice WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] Invoice ID {record_id}...")

                if existing_records:
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
                        UPDATE invoice SET
                            account_id         = %s,
                            user_id            = %s,
                            session_id         = %s,
                            payment_session_id = %s,
                            name               = %s,
                            type               = %s,
                            file_link          = %s,
                            description        = %s,
                            is_status          = %s,
                            created_by         = %s,
                            total_amount       = %s,
                            enabled            = %s,
                            timestamp          = %s,
                            updated_at         = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["payment_session_id"],
                        new_data["name"],
                        new_data["type"],
                        new_data["file_link"],
                        new_data["description"],
                        new_data["is_status"],
                        new_data["created_by"],
                        new_data["total_amount"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO invoice (
                            id, account_id, user_id, session_id, payment_session_id,
                            name, type, file_link, description, is_status,
                            created_by, total_amount, enabled,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s
                        )
                    """

                    # Use updated_at as created_at fallback
                    db.execute_query(insert_query, (
                        record_id,
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["payment_session_id"],
                        new_data["name"],
                        new_data["type"],
                        new_data["file_link"],
                        new_data["description"],
                        new_data["is_status"],
                        new_data["created_by"],
                        new_data["total_amount"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],   # fallback for created_at
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing invoice ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_invoice: {err}")

    return result


def process_invoice_session(db, invoice_data):
    """
    Process invoice data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        invoice_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING INVOICES")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if invoice_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(invoice_data['created'])} records)...")
        results["created_section"] = insert_invoice(db, invoice_data)

    # Process 'updated' section
    if invoice_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(invoice_data['updated'])} records)...")
        results["updated_section"] = update_invoice(db, invoice_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 INVOICES - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results