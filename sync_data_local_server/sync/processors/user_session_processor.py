"""
User-Session Relation Data Processor
Handles inserting and updating relation_user_session records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_user_session_relations(db, relation_data):
    """
    Handle 'created' user-session relations from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        relation_data: Dictionary with 'created' key

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
        created_relations = relation_data.get("created", [])
        result["total_processed"] = len(created_relations)

        if not created_relations:
            print("   ℹ️  No user-session relations in 'created'")
            return result

        print(f"   Processing {len(created_relations)} user-session relation(s) from 'created'...")

        for i, relation in enumerate(created_relations, 1):
            try:
                relation_id = relation.get("id")
                if not relation_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "user_id": relation.get("userId"),
                    "session_id": relation.get("sessionId"),
                    "relation_group": relation.get("relationGroup"),
                    "ref": relation.get("ref"),
                    "enabled": 1 if relation.get("enabled", True) else 0,
                    "release_token": 1 if relation.get("releaseToken", False) else 0,
                    "use_token": relation.get("useToken"),
                    "timestamp": format_date(relation.get("timestamp")),
                    "created_at": format_date(relation.get("createdAt")),
                    "updated_at": format_date(relation.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM relation_user_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (relation_id,))

                print(f"   [{i}/{len(created_relations)}] Relation ID {relation_id}...")

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
                        UPDATE relation_user_session SET
                            user_id = %s,
                            session_id = %s,
                            relation_group_local_session_id = %s,
                            ref = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s

                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["relation_group"],
                        new_data["ref"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        relation_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New relation - inserting...")

                    insert_query = """
                        INSERT INTO relation_user_session (
                            id, user_id, session_id, relation_group_local_session_id, ref,
                            enabled, releaseToken, useToken, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        relation_id,
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["relation_group"],
                        new_data["ref"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation ID {relation.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_user_session_relations: {err}")

    return result


def update_user_session_relations(db, relation_data):
    """
    Handle 'updated' user-session relations from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        relation_data: Dictionary with 'updated' key

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
        updated_relations = relation_data.get("updated", [])
        result["total_processed"] = len(updated_relations)

        if not updated_relations:
            print("   ℹ️  No user-session relations in 'updated'")
            return result

        print(f"   Processing {len(updated_relations)} user-session relation(s) from 'updated'...")

        for i, relation in enumerate(updated_relations, 1):
            try:
                relation_id = relation.get("id")
                if not relation_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "user_id": relation.get("userId"),
                    "session_id": relation.get("sessionId"),
                    "relation_group": relation.get("relationGroup"),  # This is the field name from API
                    "ref": relation.get("ref"),
                    "enabled": 1 if relation.get("enabled", True) else 0,
                    "release_token": 1 if relation.get("releaseToken", False) else 0,
                    "use_token": relation.get("useToken"),
                    "timestamp": format_date(relation.get("timestamp")),
                    "updated_at": format_date(relation.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM relation_user_session WHERE id = %s"
                existing_records = db.fetch_query(select_query, (relation_id,))

                print(f"   [{i}/{len(updated_relations)}] Relation ID {relation_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
                    has_changes = False
                    compare_fields = ["user_id", "session_id", "relation_group_local_session_id", "ref",
                                      "enabled", "releaseToken", "useToken", "timestamp", "updated_at"]

                    # Map our new_data keys to database column names
                    field_mapping = {
                        "user_id": "user_id",
                        "session_id": "session_id",
                        "relation_group": "relation_group_local_session_id",  # This is the mapping!
                        "ref": "ref",
                        "enabled": "enabled",
                        "release_token": "releaseToken",
                        "use_token": "useToken",
                        "timestamp": "timestamp",
                        "updated_at": "updated_at"
                    }

                    for new_key, db_key in field_mapping.items():
                        old_value = str(existing.get(db_key)) if existing.get(db_key) is not None else None
                        new_value = str(new_data.get(new_key)) if new_data.get(new_key) is not None else None
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
                        UPDATE relation_user_session SET
                            user_id = %s,
                            session_id = %s,
                            relation_group_local_session_id = %s,
                            ref = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["relation_group"],  # This maps to relation_group_local_session_id
                        new_data["ref"],
                        new_data["enabled"],
                        new_data["release_token"],  # This maps to releaseToken
                        new_data["use_token"],  # This maps to useToken
                        new_data["timestamp"],
                        new_data["updated_at"],
                        relation_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Relation not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO relation_user_session (
                            id, user_id, session_id, relation_group_local_session_id, ref,
                            enabled, releaseToken, useToken, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        relation_id,
                        new_data["user_id"],
                        new_data["session_id"],
                        new_data["relation_group"],  # This maps to relation_group_local_session_id
                        new_data["ref"],
                        new_data["enabled"],
                        new_data["release_token"],  # This maps to releaseToken
                        new_data["use_token"],  # This maps to useToken
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing relation ID {relation.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_user_session_relations: {err}")

    return result

def process_user_session_relations(db, relation_data):
    """
    Process user-session relation data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        relation_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING USER-SESSION RELATIONS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if relation_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(relation_data['created'])} records)...")
        results["created_section"] = insert_user_session_relations(db, relation_data)

    # Process 'updated' section
    if relation_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(relation_data['updated'])} records)...")
        results["updated_section"] = update_user_session_relations(db, relation_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 USER-SESSION RELATIONS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results