"""
Season Data Processor
Handles inserting and updating Season records in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_season(db, season_data):
    """
    Handle 'created' season records from API
    Logic:
    - Check if id_prod already exists (avoid duplicates from local pushes)
    - If record exists in DB by id → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        season_data: Dictionary with 'created' key

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
        created_records = season_data.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No Season records in 'created'")
            return result

        print(f"   Processing {len(created_records)} season record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM season WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (record_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_records)}] Season ID {record_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                # Prepare new data with safe defaults — snake_case DB columns
                # TODO: confirm column names/types against `DESCRIBE season;`
                new_data = {
                    "id_prod": record.get("id"),
                    "account_id": record.get("accountId"),
                    "formation_id": record.get("formationId"),
                    "title": record.get("title"),
                    "description": record.get("description"),
                    "number_duration": record.get("numberDuration") or "",
                    "type_duration": record.get("typeDuration") or "",
                    "ref": record.get("reference"),
                    "status": 1 if record.get("status", True) else 0,
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "created_at": format_date(record.get("createdAt")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                # Check if record exists by id
                select_query = "SELECT * FROM season WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] Season ID {record_id}...")

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
                        print(f"      ⏭️  Already exists with same data - skipped")
                        result["skipped"] += 1
                        continue

                    print(f"      🔄 Already exists but data changed - updating...")

                    update_query = """
                        UPDATE season SET
                            id_prod = %s,
                            account_id = %s,
                            formation_id = %s,
                            title = %s,
                            description = %s,
                            number_duration = %s,
                            type_duration = %s,
                            ref = %s,
                            status = %s,
                            enabled = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["title"],
                        new_data["description"],
                        new_data["number_duration"],
                        new_data["type_duration"],
                        new_data["ref"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ✨ New season - inserting...")

                    insert_query = """
                        INSERT INTO season (
                            id, id_prod, account_id, formation_id, title, description,
                            number_duration, type_duration, ref, status, enabled,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["title"],
                        new_data["description"],
                        new_data["number_duration"],
                        new_data["type_duration"],
                        new_data["ref"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing season ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_season: {err}")

    return result


def update_season(db, season_data):
    """
    Handle 'updated' season records from API
    Logic:
    - Look up by id_prod first, then by id
    - If exists → UPDATE (using local id)
    - If not → INSERT (don't skip!)

    Args:
        db: Database instance
        season_data: Dictionary with 'updated' key

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
        updated_records = season_data.get("updated", [])
        result["total_processed"] = len(updated_records)

        if not updated_records:
            print("   ℹ️  No Season records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} season record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                new_data = {
                    "id_prod": record.get("id"),
                    "account_id": record.get("accountId"),
                    "formation_id": record.get("formationId"),
                    "title": record.get("title"),
                    "description": record.get("description"),
                    "number_duration": record.get("numberDuration"),
                    "type_duration": record.get("typeDuration"),
                    "reference": record.get("reference"),
                    "status": 1 if record.get("status", True) else 0,
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "release_token": 1 if record.get("releaseToken", False) else 0,
                    "use_token": record.get("useToken"),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                check_prod_query = "SELECT * FROM season WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (record_id,))

                if not existing_records:
                    select_query = "SELECT * FROM season WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] Season ID {record_id}...")

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
                        UPDATE season SET
                            id_prod = %s,
                            account_id = %s,
                            formation_id = %s,
                            title = %s,
                            description = %s,
                            number_duration = %s,
                            type_duration = %s,
                            ref = %s,
                            status = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["title"],
                        new_data["description"],
                        new_data["number_duration"],
                        new_data["type_duration"],
                        new_data["reference"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ⚠️  Season not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO season (
                            id, id_prod, account_id, formation_id, title, description,
                            number_duration, type_duration, ref, status, enabled,
                            release_token, use_token, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["formation_id"],
                        new_data["title"],
                        new_data["description"],
                        new_data["number_duration"],
                        new_data["type_duration"],
                        new_data["reference"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["updated_at"],  # used as created_at too
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing season ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_season: {err}")

    return result


def process_season(db, season_data):
    """
    Process season data (handles both 'created' and 'updated' sections)
    """
    print("\n📌 PROCESSING SEASONS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if season_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(season_data['created'])} records)...")
        results["created_section"] = insert_season(db, season_data)

    if season_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(season_data['updated'])} records)...")
        results["updated_section"] = update_season(db, season_data)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 SEASONS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results