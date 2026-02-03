"""
Account Subject Data Processor
Handle inserting and updating account_subject recrods in the database
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date

def insert_account_subjects(db, account_subject_data):
    """
    Handle 'created' account_subjects from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        account_subject_data: Dictionary with 'created' key

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
        created_account_subjects = account_subject_data.get("created", [])
        result["total_processed"] = len(created_account_subjects)

        if not created_account_subjects:
            print("   ℹ️  No account_subjects in 'created'")
            return result

        print(f"   Processing {len(created_account_subjects)} account_subject(s) from 'created'...")

        for i, account_subject in enumerate(created_account_subjects, 1):
            try:
                account_subject_id = account_subject.get("id")
                if not account_subject_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "account_id": account_subject.get("accountId"),
                    "subject_config_id": account_subject.get("subjectConfigId"),
                    "other_subject": account_subject.get("otherSubject"),
                    "status": 1 if account_subject.get("status", True) else 0,
                    "description": account_subject.get("description", ""),
                    "enabled": 1 if account_subject.get("enabled", True) else 0,
                    "releaseToken": 1 if account_subject.get("releaseToken", False) else 0,
                    "useToken": account_subject.get("useToken"),
                    "created_at": format_date(account_subject.get("createdAt")),
                    "updated_at": format_date(account_subject.get("updatedAt")),
                    "timestamp": format_date(account_subject.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM account_subject WHERE id = %s"
                existing_records = db.fetch_query(select_query, (account_subject_id,))

                print(f"   [{i}/{len(created_account_subjects)}] Account_subject ID {account_subject_id}...")

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
                        UPDATE account_subject SET
                            account_id = %s,
                            subject_config_id = %s,
                            other_subject = %s,
                            status = %s,
                            description = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["subject_config_id"],
                        new_data["other_subject"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        account_subject_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO account_subject (
                            id, account_id, subject_config_id, other_subject, status,
                            description, enabled, releaseToken, useToken,
                            created_at, updated_at, timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        account_subject_id,
                        new_data["account_id"],
                        new_data["subject_config_id"],
                        new_data["other_subject"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account_subject ID {account_subject.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_account_subjects: {err}")

    return result



def update_account_subjects(db, account_subject_data):
    """
    Handle 'updated' account_subjects from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        account_subject_data: Dictionary with 'updated' key

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
        updated_account_subjects = account_subject_data.get("updated", [])
        result["total_processed"] = len(updated_account_subjects)

        if not updated_account_subjects:
            print("   ℹ️  No account_subjects in 'updated'")
            return result

        print(f"   Processing {len(updated_account_subjects)} account_subject(s) from 'updated'...")

        for i, account_subject in enumerate(updated_account_subjects, 1):
            try:
                account_subject_id = account_subject.get("id")
                if not account_subject_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "account_id": account_subject.get("accountId"),
                    "subject_config_id": account_subject.get("subjectConfigId"),
                    "other_subject": account_subject.get("otherSubject"),
                    "status": 1 if account_subject.get("status", True) else 0,
                    "description": account_subject.get("description", ""),
                    "enabled": 1 if account_subject.get("enabled", True) else 0,
                    "releaseToken": 1 if account_subject.get("releaseToken", False) else 0,
                    "useToken": account_subject.get("useToken"),
                    "updated_at": format_date(account_subject.get("updatedAt")),
                    "timestamp": format_date(account_subject.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM account_subject WHERE id = %s"
                existing_records = db.fetch_query(select_query, (account_subject_id,))

                print(f"   [{i}/{len(updated_account_subjects)}] Account_subject ID {account_subject_id}...")

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
                        UPDATE account_subject SET
                            account_id = %s,
                            subject_config_id = %s,
                            other_subject = %s,
                            status = %s,
                            description = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["subject_config_id"],
                        new_data["other_subject"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        account_subject_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO account_subject (
                            id, account_id, subject_config_id, other_subject, status,
                            description, enabled, releaseToken, useToken,
                            created_at, updated_at, timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use current time for created_at
                    db.execute_query(insert_query, (
                        account_subject_id,
                        new_data["account_id"],
                        new_data["subject_config_id"],
                        new_data["other_subject"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account_subject ID {account_subject.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_account_subjects: {err}")

    return result


def process_account_subjects(db, account_subject_data):
    """
    Process account_subject data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        account_subject_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING ACCOUNT_SUBJECTS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if account_subject_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(account_subject_data['created'])} records)...")
        results["created_section"] = insert_account_subjects(db, account_subject_data)

    # Process 'updated' section
    if account_subject_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(account_subject_data['updated'])} records)...")
        results["updated_section"] = update_account_subjects(db, account_subject_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 ACCOUNT_SUBJECTS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results
