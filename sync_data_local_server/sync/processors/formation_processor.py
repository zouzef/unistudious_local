"""
Formation Data Processor
Handles inserting and updating formation records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_formations(db, formation_data):
    """
    Handle 'created' formations from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        formation_data: Dictionary with 'created' key

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
        created_formations = formation_data.get("created", [])
        result["total_processed"] = len(created_formations)

        if not created_formations:
            print("   ℹ️  No formations in 'created'")
            return result

        print(f"   Processing {len(created_formations)} formation(s) from 'created'...")

        for i, formation in enumerate(created_formations, 1):
            try:
                formation_id = formation.get("id")
                if not formation_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "account_id": formation.get("accountId"),
                    "account_level_id": formation.get("accountLevelId"),
                    "account_section_id": formation.get("accountSectionId"),
                    "name": formation.get("name", ""),
                    "description": formation.get("description", ""),
                    "type_date": formation.get("type_date", ""),
                    "other_type_date": formation.get("other_type_date"),
                    "type_session": formation.get("type_session", ""),
                    "other_type_session": formation.get("other_type_session"),
                    "number_day_duration": formation.get("number_day_duration"),
                    "number_session": formation.get("number_session"),
                    "condition_of_passage": formation.get("condition_of_passage", ""),
                    "condition_of_passage_formule": formation.get("condition_of_passage_formule"),
                    "condition_of_passage_formule_by_note": formation.get("condition_of_passage_formule_by_note"),
                    "condition_of_passage_formule_by_present": formation.get("condition_of_passage_formule_by_present"),
                    "condition_of_passage_formule_by_note_present": formation.get("condition_of_passage_formule_by_note_present"),
                    "img_link": formation.get("img_link", ""),
                    "public_resource": formation.get("public_resource", "0"),
                    "status": 1 if formation.get("status", True) else 0,
                    "enabled": 1 if formation.get("enabled", True) else 0,
                    "timestamp": format_date(formation.get("timestamp")),
                    "created_at": format_date(formation.get("createdAt")),
                    "updated_at": format_date(formation.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM formation WHERE id = %s"
                existing_records = db.fetch_query(select_query, (formation_id,))

                print(f"   [{i}/{len(created_formations)}] Formation ID {formation_id}...")

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
                        UPDATE formation SET
                            account_id = %s,
                            account_level_id = %s,
                            account_section_id = %s,
                            name = %s,
                            description = %s,
                            type_date = %s,
                            other_type_date = %s,
                            type_session = %s,
                            other_type_session = %s,
                            number_day_duration = %s,
                            number_session = %s,
                            condition_of_passage = %s,
                            condition_of_passage_formule = %s,
                            condition_of_passage_formule_by_note = %s,
                            condition_of_passage_formule_by_present = %s,
                            condition_of_passage_formule_by_note_present = %s,
                            img_link = %s,
                            public_resource = %s,
                            status = %s,
                            enabled = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s,
                            is_sync = 1
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["account_level_id"],
                        new_data["account_section_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["type_date"],
                        new_data["other_type_date"],
                        new_data["type_session"],
                        new_data["other_type_session"],
                        new_data["number_day_duration"],
                        new_data["number_session"],
                        new_data["condition_of_passage"],
                        new_data["condition_of_passage_formule"],
                        new_data["condition_of_passage_formule_by_note"],
                        new_data["condition_of_passage_formule_by_present"],
                        new_data["condition_of_passage_formule_by_note_present"],
                        new_data["img_link"],
                        new_data["public_resource"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        formation_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO formation (
                            id, account_id, account_level_id, account_section_id, name, description,
                            type_date, other_type_date, type_session, other_type_session,
                            number_day_duration, number_session, condition_of_passage,
                            condition_of_passage_formule, condition_of_passage_formule_by_note,
                            condition_of_passage_formule_by_present, condition_of_passage_formule_by_note_present,
                            img_link, public_resource, status, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        formation_id,
                        new_data["account_id"],
                        new_data["account_level_id"],
                        new_data["account_section_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["type_date"],
                        new_data["other_type_date"],
                        new_data["type_session"],
                        new_data["other_type_session"],
                        new_data["number_day_duration"],
                        new_data["number_session"],
                        new_data["condition_of_passage"],
                        new_data["condition_of_passage_formule"],
                        new_data["condition_of_passage_formule_by_note"],
                        new_data["condition_of_passage_formule_by_present"],
                        new_data["condition_of_passage_formule_by_note_present"],
                        new_data["img_link"],
                        new_data["public_resource"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing formation ID {formation.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_formations: {err}")

    return result


def update_formations(db, formation_data):
    """
    Handle 'updated' formations from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        formation_data: Dictionary with 'updated' key

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
        updated_formations = formation_data.get("updated", [])
        result["total_processed"] = len(updated_formations)

        if not updated_formations:
            print("   ℹ️  No formations in 'updated'")
            return result

        print(f"   Processing {len(updated_formations)} formation(s) from 'updated'...")

        for i, formation in enumerate(updated_formations, 1):
            try:
                formation_id = formation.get("id")
                if not formation_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "account_id": formation.get("accountId"),
                    "account_level_id": formation.get("accountLevelId"),
                    "account_section_id": formation.get("accountSectionId"),
                    "name": formation.get("name", ""),
                    "description": formation.get("description", ""),
                    "type_date": formation.get("type_date", ""),
                    "other_type_date": formation.get("other_type_date"),
                    "type_session": formation.get("type_session", ""),
                    "other_type_session": formation.get("other_type_session"),
                    "number_day_duration": formation.get("number_day_duration"),
                    "number_session": formation.get("number_session"),
                    "condition_of_passage": formation.get("condition_of_passage", ""),
                    "condition_of_passage_formule": formation.get("condition_of_passage_formule"),
                    "condition_of_passage_formule_by_note": formation.get("condition_of_passage_formule_by_note"),
                    "condition_of_passage_formule_by_present": formation.get("condition_of_passage_formule_by_present"),
                    "condition_of_passage_formule_by_note_present": formation.get("condition_of_passage_formule_by_note_present"),
                    "img_link": formation.get("img_link", ""),
                    "public_resource": formation.get("public_resource", "0"),
                    "status": 1 if formation.get("status", True) else 0,
                    "enabled": 1 if formation.get("enabled", True) else 0,
                    "timestamp": format_date(formation.get("timestamp")),
                    "updated_at": format_date(formation.get("updatedAt"))
                }

                # Check if record exists
                select_query = "SELECT * FROM formation WHERE id = %s"
                existing_records = db.fetch_query(select_query, (formation_id,))

                print(f"   [{i}/{len(updated_formations)}] Formation ID {formation_id}...")

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
                        UPDATE formation SET
                            account_id = %s,
                            account_level_id = %s,
                            account_section_id = %s,
                            name = %s,
                            description = %s,
                            type_date = %s,
                            other_type_date = %s,
                            type_session = %s,
                            other_type_session = %s,
                            number_day_duration = %s,
                            number_session = %s,
                            condition_of_passage = %s,
                            condition_of_passage_formule = %s,
                            condition_of_passage_formule_by_note = %s,
                            condition_of_passage_formule_by_present = %s,
                            condition_of_passage_formule_by_note_present = %s,
                            img_link = %s,
                            public_resource = %s,
                            status = %s,
                            enabled = %s,
                            timestamp = %s,
                            updated_at = %s,
                            is_sync = 1
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["account_id"],
                        new_data["account_level_id"],
                        new_data["account_section_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["type_date"],
                        new_data["other_type_date"],
                        new_data["type_session"],
                        new_data["other_type_session"],
                        new_data["number_day_duration"],
                        new_data["number_session"],
                        new_data["condition_of_passage"],
                        new_data["condition_of_passage_formule"],
                        new_data["condition_of_passage_formule_by_note"],
                        new_data["condition_of_passage_formule_by_present"],
                        new_data["condition_of_passage_formule_by_note_present"],
                        new_data["img_link"],
                        new_data["public_resource"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        formation_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO formation (
                            id, account_id, account_level_id, account_section_id, name, description,
                            type_date, other_type_date, type_session, other_type_session,
                            number_day_duration, number_session, condition_of_passage,
                            condition_of_passage_formule, condition_of_passage_formule_by_note,
                            condition_of_passage_formule_by_present, condition_of_passage_formule_by_note_present,
                            img_link, public_resource, status, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        formation_id,
                        new_data["account_id"],
                        new_data["account_level_id"],
                        new_data["account_section_id"],
                        new_data["name"],
                        new_data["description"],
                        new_data["type_date"],
                        new_data["other_type_date"],
                        new_data["type_session"],
                        new_data["other_type_session"],
                        new_data["number_day_duration"],
                        new_data["number_session"],
                        new_data["condition_of_passage"],
                        new_data["condition_of_passage_formule"],
                        new_data["condition_of_passage_formule_by_note"],
                        new_data["condition_of_passage_formule_by_present"],
                        new_data["condition_of_passage_formule_by_note_present"],
                        new_data["img_link"],
                        new_data["public_resource"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing formation ID {formation.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_formations: {err}")

    return result


def process_formations(db, formation_data):
    """
    Process formation data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        formation_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING FORMATIONS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if formation_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(formation_data['created'])} records)...")
        results["created_section"] = insert_formations(db, formation_data)

    # Process 'updated' section
    if formation_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(formation_data['updated'])} records)...")
        results["updated_section"] = update_formations(db, formation_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 FORMATIONS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results