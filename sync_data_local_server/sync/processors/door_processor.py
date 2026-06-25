"""
SlcDoor Data Processor
Handles inserting and updating SlcDoor records in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_slc_door(db, slc_door_data):
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        created_records = slc_door_data.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No SlcDoor records in 'created'")
            return result

        print(f"   Processing {len(created_records)} slc_door record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM slc_door WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (record_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_records)}] SlcDoor ID {record_id} already exists as id_prod "
                          f"(local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                new_data = {
                    "id_prod": record.get("id"),
                    "slc_id": record.get("slcId"),
                    "room_id": record.get("roomId"),
                    "name": record.get("name"),
                    "mac_id": record.get("mac_id"),
                    "password": record.get("password"),
                    "status": record.get("status", "False"),
                    "oc": 1 if record.get("oc", False) else 0,
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "timestamp": format_date(record.get("timestamp")),
                    "created_at": format_date(record.get("createdAt")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                select_query = "SELECT * FROM slc_door WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] SlcDoor ID {record_id}...")

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
                        UPDATE slc_door SET
                            id_prod = %s,
                            slc_id = %s,
                            room_id = %s,
                            name = %s,
                            mac_id = %s,
                            password = %s,
                            status = %s,
                            oc = %s,
                            enabled = %s,
                            timestamp = %s,
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
                        new_data["password"],
                        new_data["status"],
                        new_data["oc"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ✨ New slc_door - inserting...")

                    insert_query = """
                        INSERT INTO slc_door (
                            id, id_prod, slc_id, room_id, name, mac_id, password,
                            status, oc, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["oc"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing slc_door ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_slc_door: {err}")

    return result


def update_slc_door(db, slc_door_data):
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        updated_records = slc_door_data.get("updated", [])
        result["total_processed"] = len(updated_records)

        if not updated_records:
            print("   ℹ️  No SlcDoor records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} slc_door record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                new_data = {
                    "id_prod": record.get("id"),
                    "slc_id": record.get("slcId"),
                    "room_id": record.get("roomId"),
                    "name": record.get("name"),
                    "mac_id": record.get("mac_id"),
                    "password": record.get("password"),
                    "status": record.get("status", "False"),
                    "oc": 1 if record.get("oc", False) else 0,
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "timestamp": format_date(record.get("timestamp")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                # Look up by id_prod first, then fall back to id
                check_prod_query = "SELECT * FROM slc_door WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (record_id,))

                if not existing_records:
                    select_query = "SELECT * FROM slc_door WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] SlcDoor ID {record_id}...")

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
                        UPDATE slc_door SET
                            id_prod = %s,
                            slc_id = %s,
                            room_id = %s,
                            name = %s,
                            mac_id = %s,
                            password = %s,
                            status = %s,
                            oc = %s,
                            enabled = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["oc"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ⚠️  SlcDoor not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO slc_door (
                            id, id_prod, slc_id, room_id, name, mac_id, password,
                            status, oc, enabled, timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["slc_id"],
                        new_data["room_id"],
                        new_data["name"],
                        new_data["mac_id"],
                        new_data["password"],
                        new_data["status"],
                        new_data["oc"],
                        new_data["enabled"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # used as created_at too
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing slc_door ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_slc_door: {err}")

    return result


def process_slc_door(db, slc_door_data):
    """
    Process slc_door data (handles both 'created' and 'updated' sections)
    """
    print("\n📌 PROCESSING SLC DOORS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if slc_door_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(slc_door_data['created'])} record(s))...")
        results["created_section"] = insert_slc_door(db, slc_door_data)

    if slc_door_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(slc_door_data['updated'])} record(s))...")
        results["updated_section"] = update_slc_door(db, slc_door_data)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 SLC DOORS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results