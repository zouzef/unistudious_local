"""
Subject Data Processor
Handles inserting and updating subject records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_subjects(db, subject_data):
    """
    Handle 'created' subjects from API
    Logic:
    - If subject exists in DB → UPDATE it
    - If subject does NOT exist → INSERT it

    Args:
        db: Database instance
        subject_data: Dictionary with 'created' key

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
        created_subjects = subject_data.get("created", [])
        result["total_processed"] = len(created_subjects)

        if not created_subjects:
            print("   ℹ️  No subjects in 'created'")
            return result

        print(f"   Processing {len(created_subjects)} subject(s) from 'created'...")

        for i, subject in enumerate(created_subjects, 1):
            try:
                subject_id = subject.get("id")
                if not subject_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "name": subject.get("name", ""),
                    "status": 1 if subject.get("status", True) else 0,
                    "description": subject.get("description", ""),
                    "enabled": 1 if subject.get("enabled", True) else 0,
                    "releaseToken": 1 if subject.get("releaseToken", False) else 0,
                    "useToken": subject.get("useToken"),
                    "timestamp": format_date(subject.get("timestamp")),
                    "created_at": format_date(subject.get("createdAt")),
                    "updated_at": format_date(subject.get("updatedAt"))
                }

                # Check if subject exists
                select_query = "SELECT * FROM subject_config WHERE id = %s"
                existing_records = db.fetch_query(select_query, (subject_id,))

                print(f"   [{i}/{len(created_subjects)}] Subject ID {subject_id}...")

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
                        UPDATE subject_config SET
                            name = %s,
                            status = %s,
                            description = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["name"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        subject_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New subject - inserting...")

                    insert_query = """
                        INSERT INTO subject_config (
                            id, name, status, description, enabled,
                            releaseToken, useToken, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        subject_id,
                        new_data["name"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing subject ID {subject.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_subjects: {err}")

    return result


def update_subjects(db, subject_data):
    """
    Handle 'updated' subjects from API
    Logic:
    - If subject exists in DB → UPDATE it
    - If subject does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        subject_data: Dictionary with 'updated' key

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
        updated_subjects = subject_data.get("updated", [])
        result["total_processed"] = len(updated_subjects)

        if not updated_subjects:
            print("   ℹ️  No subjects in 'updated'")
            return result

        print(f"   Processing {len(updated_subjects)} subject(s) from 'updated'...")

        for i, subject in enumerate(updated_subjects, 1):
            try:
                subject_id = subject.get("id")
                if not subject_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "name": subject.get("name"),
                    "status": 1 if subject.get("status", True) else 0,
                    "description": subject.get("description"),
                    "enabled": 1 if subject.get("enabled", True) else 0,
                    "releaseToken": 1 if subject.get("releaseToken", False) else 0,
                    "useToken": subject.get("useToken"),
                    "timestamp": format_date(subject.get("timestamp")),
                    "updated_at": format_date(subject.get("updatedAt"))
                }

                # Check if subject exists
                select_query = "SELECT * FROM subject_config WHERE id = %s"
                existing_records = db.fetch_query(select_query, (subject_id,))

                print(f"   [{i}/{len(updated_subjects)}] Subject ID {subject_id}...")

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
                        UPDATE subject_config SET
                            name = %s,
                            status = %s,
                            description = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["name"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        subject_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Subject not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO subject_config (
                            id, name, status, description, enabled,
                            releaseToken, useToken, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        subject_id,
                        new_data["name"],
                        new_data["status"],
                        new_data["description"],
                        new_data["enabled"],
                        new_data["releaseToken"],
                        new_data["useToken"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing subject ID {subject.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_subjects: {err}")

    return result


def process_subjects(db, subject_data):
    """
    Process subject data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        subject_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING SUBJECTS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if subject_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(subject_data['created'])} records)...")
        results["created_section"] = insert_subjects(db, subject_data)

    # Process 'updated' section
    if subject_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(subject_data['updated'])} records)...")
        results["updated_section"] = update_subjects(db, subject_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 SUBJECTS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results