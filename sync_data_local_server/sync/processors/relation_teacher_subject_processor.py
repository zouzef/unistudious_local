"""
Teacher-Subject Relation Data Processor
Handles inserting and updating relation_teacher_to_subject_group records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_teacher_subject_relations(db, relation_data):
    """
    Handle 'created' teacher-subject relations from API
    Logic:
    - If record exists in DB (matched by its own id / external_id) → UPDATE it
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
            print("   ℹ️  No teacher-subject relations in 'created'")
            return result

        print(f"   Processing {len(created_relations)} teacher-subject relation(s) from 'created'...")

        for i, relation in enumerate(created_relations, 1):
            try:
                external_id = relation.get("id")
                if not external_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "id": relation.get("id"),
                    "group_id": relation.get("groupId"),
                    "subject_id": relation.get("subjectId"),
                    "teacher_id": relation.get("teacherId"),
                    "enabled": 1 if relation.get("enabled", True) else 0,
                    "release_token": 1 if relation.get("releaseToken", False) else 0,
                    "use_token": relation.get("useToken"),
                    "timestamp": format_date(relation.get("timestamp")),
                    "created_at": format_date(relation.get("createdAt")),
                    "updated_at": format_date(relation.get("updatedAt"))
                }

                # Check if record exists — match on the record's own stable id,
                # NOT on group_id/subject_id/teacher_id. Those fields (especially
                # teacher_id) are exactly what can change on an "updated" record,
                # so matching on them would make an existing row look "new".
                select_query = """
                    SELECT * FROM relation_teacher_to_subject_group
                    WHERE id = %s
                """
                existing_records = db.fetch_query(select_query, (external_id,))

                print(f"   [{i}/{len(created_relations)}] External ID {external_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
                    has_changes = False
                    comparison_fields = ["group_id", "subject_id", "teacher_id", "enabled",
                                          "release_token", "use_token", "timestamp", "updated_at"]
                    field_to_column = {
                        "group_id": "relation_group_local_session_id",
                        "subject_id": "subject_id",
                        "teacher_id": "user_id",
                        "enabled": "enabled",
                        "release_token": "releaseToken",
                        "use_token": "useToken",
                        "timestamp": "timestamp",
                        "updated_at": "updated_at",
                    }
                    for field in comparison_fields:
                        column = field_to_column[field]
                        old_value = str(existing.get(column)) if existing.get(column) is not None else None
                        new_value = str(new_data.get(field)) if new_data.get(field) is not None else None
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
                        UPDATE relation_teacher_to_subject_group SET
                            relation_group_local_session_id = %s,
                            subject_id = %s,
                            user_id = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    success = db.execute_query(update_query, (
                        new_data["group_id"],
                        new_data["subject_id"],
                        new_data["teacher_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    if success:
                        result["updated"] += 1
                        print(f"      ✅ Updated successfully (Internal ID: {existing['id']})")
                    else:
                        result["errors"] += 1
                        print(f"      ❌ Update failed for external ID {external_id}")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New relation - inserting...")

                    insert_query = """
                        INSERT INTO relation_teacher_to_subject_group (
                            id,relation_group_local_session_id, subject_id, user_id,
                            enabled, releaseToken, useToken, timestamp, created_at, updated_at, slc_use, id_prod
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
                    """

                    success = db.execute_query(insert_query, (
                        external_id,
                        new_data["group_id"],
                        new_data["subject_id"],
                        new_data["teacher_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        external_id,  # id_prod
                    ))

                    if success:
                        result["inserted"] += 1
                        print(f"      ✅ Inserted successfully")
                    else:
                        result["errors"] += 1
                        print(f"      ❌ Insert failed for external ID {external_id}")

            except Exception as err:
                print(f"      ❌ Error processing external ID {relation.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_teacher_subject_relations: {err}")

    return result


def update_teacher_subject_relations(db, relation_data):
    """
    Handle 'updated' teacher-subject relations from API
    Logic:
    - If record exists in DB (matched by its own id / external_id) → UPDATE it
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
            print("   ℹ️  No teacher-subject relations in 'updated'")
            return result

        print(f"   Processing {len(updated_relations)} teacher-subject relation(s) from 'updated'...")

        for i, relation in enumerate(updated_relations, 1):
            try:
                external_id = relation.get("id")
                if not external_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "group_id": relation.get("groupId"),
                    "subject_id": relation.get("subjectId"),
                    "teacher_id": relation.get("teacherId"),
                    "enabled": 1 if relation.get("enabled", True) else 0,
                    "release_token": 1 if relation.get("releaseToken", False) else 0,
                    "use_token": relation.get("useToken"),
                    "timestamp": format_date(relation.get("timestamp")),
                    "updated_at": format_date(relation.get("updatedAt"))
                }

                # Check if record exists — match on the record's own stable id,
                # NOT on group_id/subject_id/teacher_id. A teacher reassignment
                # changes teacher_id, so matching on it would make an existing
                # row look "not found" and trigger a duplicate-key INSERT instead
                # of the correct UPDATE.
                select_query = """
                    SELECT * FROM relation_teacher_to_subject_group
                    WHERE id = %s
                """
                existing_records = db.fetch_query(select_query, (external_id,))

                print(f"   [{i}/{len(updated_relations)}] External ID {external_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
                    has_changes = False
                    comparison_fields = ["group_id", "subject_id", "teacher_id", "enabled",
                                          "release_token", "use_token", "timestamp", "updated_at"]
                    field_to_column = {
                        "group_id": "relation_group_local_session_id",
                        "subject_id": "subject_id",
                        "teacher_id": "user_id",
                        "enabled": "enabled",
                        "release_token": "releaseToken",
                        "use_token": "useToken",
                        "timestamp": "timestamp",
                        "updated_at": "updated_at",
                    }
                    for field in comparison_fields:
                        column = field_to_column[field]
                        old_value = str(existing.get(column)) if existing.get(column) is not None else None
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
                        UPDATE relation_teacher_to_subject_group SET
                            relation_group_local_session_id = %s,
                            subject_id = %s,
                            user_id = %s,
                            enabled = %s,
                            releaseToken = %s,
                            useToken = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    success = db.execute_query(update_query, (
                        new_data["group_id"],
                        new_data["subject_id"],
                        new_data["teacher_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    if success:
                        result["updated"] += 1
                        print(f"      ✅ Updated successfully (Internal ID: {existing['id']})")
                    else:
                        result["errors"] += 1
                        print(f"      ❌ Update failed for external ID {external_id}")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Relation not found in DB - inserting...")

                    insert_query = """
                            INSERT INTO relation_teacher_to_subject_group (
                            id, relation_group_local_session_id, subject_id, user_id,
                            enabled, releaseToken, useToken, timestamp, created_at, updated_at, slc_use, id_prod
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    success = db.execute_query(insert_query, (
                        external_id,  # id
                        new_data["group_id"],
                        new_data["subject_id"],
                        new_data["teacher_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        new_data["updated_at"],
                        external_id,  # id_prod
                    ))

                    if success:
                        result["inserted"] += 1
                        print(f"      ✅ Inserted successfully")
                    else:
                        result["errors"] += 1
                        print(f"      ❌ Insert failed for external ID {external_id}")

            except Exception as err:
                print(f"      ❌ Error processing external ID {relation.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_teacher_subject_relations: {err}")

    return result


def process_teacher_subject_relations(db, relation_data):
    """
    Process teacher-subject relation data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        relation_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING TEACHER-SUBJECT RELATIONS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if relation_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(relation_data['created'])} records)...")
        results["created_section"] = insert_teacher_subject_relations(db, relation_data)

    # Process 'updated' section
    if relation_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(relation_data['updated'])} records)...")
        results["updated_section"] = update_teacher_subject_relations(db, relation_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 TEACHER-SUBJECT RELATIONS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results