"""
Camera Data Processor
Handles inserting and updating camera records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_cameras(db, camera_data):
    """
    Handle 'created' cameras from API
    Logic:
    - Check if id_prod already exists (avoid duplicates from local pushes)
    - If record exists in DB by id → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        camera_data: Dictionary with 'created' key

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
        created_cameras = camera_data.get("created", [])
        result["total_processed"] = len(created_cameras)

        if not created_cameras:
            print("   ℹ️  No cameras in 'created'")
            return result

        print(f"   Processing {len(created_cameras)} camera(s) from 'created'...")

        for i, camera in enumerate(created_cameras, 1):
            try:
                camera_id = camera.get("id")
                if not camera_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM camera WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (camera_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_cameras)}] Camera ID {camera_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                # Prepare new data
                new_data = {
                    "id_prod":    camera.get("id"),
                    "slc_id":     camera.get("slcId"),
                    "room_id":    camera.get("roomId"),
                    "name":       camera.get("name", ""),
                    "mac_id":     camera.get("mac_id", ""),
                    "username":   camera.get("username", ""),
                    "password":   camera.get("password", ""),
                    "type":       camera.get("type", "webcam"),
                    "status":     camera.get("status", "Active"),
                    "enabled":    1 if camera.get("enabled", True) else 0,
                    "timestamp":  format_date(camera.get("timestamp")),
                    "created_at": format_date(camera.get("createdAt")),
                    "updated_at": format_date(camera.get("updatedAt"))
                }

                # Check if record exists by id
                select_query = "SELECT * FROM camera WHERE id = %s"
                existing_records = db.fetch_query(select_query, (camera_id,))

                print(f"   [{i}/{len(created_cameras)}] Camera ID {camera_id}...")

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
                        UPDATE camera SET
                            id_prod    = %s,
                            slc_id     = %s,
                            room_id    = %s,
                            name       = %s,
                            mac_id     = %s,
                            username   = %s,
                            password   = %s,
                            type       = %s,
                            status     = %s,
                            enabled    = %s,
                            timestamp  = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["username"],
                        new_data["password"],
                        new_data["type"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        camera_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    insert_query = """
                        INSERT INTO camera (
                            id, id_prod, slc_id, room_id, name, mac_id, username, password,
                            type, status, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        camera_id,
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["username"],
                        new_data["password"],
                        new_data["type"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing camera ID {camera.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_cameras: {err}")

    return result


def update_cameras(db, camera_data):
    """
    Handle 'updated' cameras from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        camera_data: Dictionary with 'updated' key

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
        updated_cameras = camera_data.get("updated", [])
        result["total_processed"] = len(updated_cameras)

        if not updated_cameras:
            print("   ℹ️  No cameras in 'updated'")
            return result

        print(f"   Processing {len(updated_cameras)} camera(s) from 'updated'...")

        for i, camera in enumerate(updated_cameras, 1):
            try:
                camera_id = camera.get("id")
                if not camera_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "id_prod":    camera.get("id"),
                    "slc_id":     camera.get("slcId"),
                    "room_id":    camera.get("roomId"),
                    "name":       camera.get("name", ""),
                    "mac_id":     camera.get("mac_id", ""),
                    "username":   camera.get("username", ""),
                    "password":   camera.get("password", ""),
                    "type":       camera.get("type", "webcam"),
                    "status":     camera.get("status", "Active"),
                    "enabled":    1 if camera.get("enabled", True) else 0,
                    "timestamp":  format_date(camera.get("timestamp")),
                    "updated_at": format_date(camera.get("updatedAt"))
                }

                # ✅ Check by id_prod first, then fall back to id
                check_prod_query = "SELECT * FROM camera WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (camera_id,))

                if not existing_records:
                    select_query = "SELECT * FROM camera WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (camera_id,))

                print(f"   [{i}/{len(updated_cameras)}] Camera ID {camera_id}...")

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
                        UPDATE camera SET
                            id_prod    = %s,
                            slc_id     = %s,
                            room_id    = %s,
                            name       = %s,
                            mac_id     = %s,
                            username   = %s,
                            password   = %s,
                            type       = %s,
                            status     = %s,
                            enabled    = %s,
                            timestamp  = %s,
                            updated_at = %s,
                            is_sync    = 1
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["username"],
                        new_data["password"],
                        new_data["type"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        existing["id"]  # ← use actual local id (handles both cases)
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO camera (
                            id, id_prod, slc_id, room_id, name, mac_id, username, password,
                            type, status, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        camera_id,
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["username"],
                        new_data["password"],
                        new_data["type"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # fallback for created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing camera ID {camera.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_cameras: {err}")

    return result


def process_cameras(db, camera_data):
    """
    Process camera data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        camera_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING CAMERAS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if camera_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(camera_data['created'])} records)...")
        results["created_section"] = insert_cameras(db, camera_data)

    # Process 'updated' section
    if camera_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(camera_data['updated'])} records)...")
        results["updated_section"] = update_cameras(db, camera_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 CAMERAS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results