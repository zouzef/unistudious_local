"""
Local and Room Data Processor
Handles inserting and updating local and room records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_local_and_rooms(db, local_data):
    """
    Handle 'created' locals and rooms from API
    Logic:
    - If local exists in DB → UPDATE it (and its rooms)
    - If local does NOT exist → INSERT it (and its rooms)

    Args:
        db: Database instance
        local_data: Dictionary with 'created' key

    Returns:
        dict: Statistics (inserted, updated, skipped, errors) for locals and rooms
    """
    result = {
        "locals_inserted": 0,
        "locals_updated": 0,
        "locals_skipped": 0,
        "rooms_inserted": 0,
        "rooms_updated": 0,
        "rooms_skipped": 0,
        "errors": 0,
        "total_locals_processed": 0,
        "total_rooms_processed": 0
    }

    try:
        created_locals = local_data.get("created", [])
        result["total_locals_processed"] = len(created_locals)

        if not created_locals:
            print("   ℹ️  No locals in 'created'")
            return result

        print(f"   Processing {len(created_locals)} local(s) from 'created'...")

        for i, local in enumerate(created_locals, 1):
            try:
                local_id = local.get("id")
                if not local_id:
                    raise ValueError("Missing required field: id")

                # Prepare new local data
                new_local_data = {
                    "account_id": local.get("accountId"),
                    "name": local.get("name", ""),
                    "address": local.get("address", ""),
                    "gps": local.get("gps", ""),
                    "status": 1 if local.get("status", True) else 0,
                    "enabled": 1 if local.get("enabled", True) else 0,
                    "default_local": 1 if local.get("default", False) else 0,
                    "created_at": format_date(local.get("createdAt")),
                    "updated_at": format_date(local.get("updatedAt"))
                }

                # Get rooms data
                rooms = local.get("rooms", [])
                result["total_rooms_processed"] += len(rooms)

                # Check if local exists
                select_query = "SELECT * FROM local WHERE id = %s"
                existing_local_records = db.fetch_query(select_query, (local_id,))

                print(f"   [{i}/{len(created_locals)}] Local ID {local_id}...")

                if existing_local_records:
                    # LOCAL EXISTS → Compare and UPDATE if different
                    existing_local = existing_local_records[0]

                    # Compare local data
                    local_has_changes = False
                    for key, value in new_local_data.items():
                        old_value = str(existing_local.get(key)) if existing_local.get(key) is not None else None
                        new_value = str(value) if value is not None else None
                        if old_value != new_value:
                            local_has_changes = True
                            break

                    if not local_has_changes and not rooms:
                        print(f"      ⏭️  Local already exists with same data and no rooms - skipped")
                        result["locals_skipped"] += 1
                        continue

                    if local_has_changes:
                        # Update local
                        print(f"      🔄 Local data changed - updating...")
                        update_query = """
                            UPDATE local SET
                                account_id = %s,
                                name = %s,
                                address = %s,
                                gps = %s,
                                status = %s,
                                enabled = %s,
                                default_local = %s,
                                created_at = %s,
                                updated_at = %s
                            WHERE id = %s
                        """
                        db.execute_query(update_query, (
                            new_local_data["account_id"],
                            new_local_data["name"],
                            new_local_data["address"],
                            new_local_data["gps"],
                            new_local_data["status"],
                            new_local_data["enabled"],
                            new_local_data["default_local"],
                            new_local_data["created_at"],
                            new_local_data["updated_at"],
                            local_id
                        ))
                        result["locals_updated"] += 1
                        print(f"      ✅ Local updated successfully")
                    else:
                        result["locals_skipped"] += 1
                        print(f"      ⏭️  Local data identical - skipped update")

                    # Process rooms for existing local
                    room_stats = process_rooms_for_local(db, local_id, rooms, "created")
                    result["rooms_inserted"] += room_stats["inserted"]
                    result["rooms_updated"] += room_stats["updated"]
                    result["rooms_skipped"] += room_stats["skipped"]

                else:
                    # LOCAL DOES NOT EXIST → INSERT
                    print(f"      ✨ New local - inserting...")

                    insert_query = """
                        INSERT INTO local (
                            id, account_id, name, address, gps, status, enabled, 
                            default_local, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    db.execute_query(insert_query, (
                        local_id,
                        new_local_data["account_id"],
                        new_local_data["name"],
                        new_local_data["address"],
                        new_local_data["gps"],
                        new_local_data["status"],
                        new_local_data["enabled"],
                        new_local_data["default_local"],
                        new_local_data["created_at"],
                        new_local_data["updated_at"]
                    ))
                    result["locals_inserted"] += 1
                    print(f"      ✅ Local inserted successfully")

                    # Process rooms for new local
                    room_stats = process_rooms_for_local(db, local_id, rooms, "created")
                    result["rooms_inserted"] += room_stats["inserted"]
                    result["rooms_updated"] += room_stats["updated"]
                    result["rooms_skipped"] += room_stats["skipped"]

            except Exception as err:
                print(f"      ❌ Error processing local ID {local.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Locals: {result['locals_inserted']} inserted, "
              f"{result['locals_updated']} updated, {result['locals_skipped']} skipped | "
              f"Rooms: {result['rooms_inserted']} inserted, {result['rooms_updated']} updated, "
              f"{result['rooms_skipped']} skipped | Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_local_and_rooms: {err}")

    return result


def update_local_and_rooms(db, local_data):
    """
    Handle 'updated' locals and rooms from API
    Logic:
    - If local exists in DB → UPDATE it
    - If local does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        local_data: Dictionary with 'updated' key

    Returns:
        dict: Statistics (inserted, updated, skipped, errors) for locals and rooms
    """
    result = {
        "locals_inserted": 0,
        "locals_updated": 0,
        "locals_skipped": 0,
        "rooms_inserted": 0,
        "rooms_updated": 0,
        "rooms_skipped": 0,
        "errors": 0,
        "total_locals_processed": 0,
        "total_rooms_processed": 0
    }

    try:
        updated_locals = local_data.get("updated", [])
        result["total_locals_processed"] = len(updated_locals)

        if not updated_locals:
            print("   ℹ️  No locals in 'updated'")
            return result

        print(f"   Processing {len(updated_locals)} local(s) from 'updated'...")

        for i, local in enumerate(updated_locals, 1):
            try:
                local_id = local.get("id")
                if not local_id:
                    raise ValueError("Missing required field: id")

                # Prepare new local data
                new_local_data = {
                    "account_id": local.get("accountId"),
                    "name": local.get("name", ""),
                    "address": local.get("address", ""),
                    "gps": local.get("gps", ""),
                    "status": 1 if local.get("status", True) else 0,
                    "enabled": 1 if local.get("enabled", True) else 0,
                    "default_local": 1 if local.get("default", False) else 0,
                    "updated_at": format_date(local.get("updatedAt"))
                }

                # Get rooms data
                rooms = local.get("rooms", [])
                result["total_rooms_processed"] += len(rooms)

                # Check if local exists
                select_query = "SELECT * FROM local WHERE id = %s"
                existing_local_records = db.fetch_query(select_query, (local_id,))

                print(f"   [{i}/{len(updated_locals)}] Local ID {local_id}...")

                if existing_local_records:
                    # LOCAL EXISTS → Compare and UPDATE if different
                    existing_local = existing_local_records[0]

                    # Compare local data
                    local_has_changes = False
                    for key, value in new_local_data.items():
                        old_value = str(existing_local.get(key)) if existing_local.get(key) is not None else None
                        new_value = str(value) if value is not None else None
                        if old_value != new_value:
                            local_has_changes = True
                            break

                    if not local_has_changes and not rooms:
                        print(f"      ⏭️  Local data is identical and no rooms - skipped")
                        result["locals_skipped"] += 1
                        continue

                    if local_has_changes:
                        # Update local
                        print(f"      🔄 Local data changed - updating...")
                        update_query = """
                            UPDATE local SET
                                account_id = %s,
                                name = %s,
                                address = %s,
                                gps = %s,
                                status = %s,
                                enabled = %s,
                                default_local = %s,
                                updated_at = %s
                            WHERE id = %s
                        """
                        db.execute_query(update_query, (
                            new_local_data["account_id"],
                            new_local_data["name"],
                            new_local_data["address"],
                            new_local_data["gps"],
                            new_local_data["status"],
                            new_local_data["enabled"],
                            new_local_data["default_local"],
                            new_local_data["updated_at"],
                            local_id
                        ))
                        result["locals_updated"] += 1
                        print(f"      ✅ Local updated successfully")
                    else:
                        result["locals_skipped"] += 1
                        print(f"      ⏭️  Local data identical - skipped update")

                    # Process rooms for existing local
                    room_stats = process_rooms_for_local(db, local_id, rooms, "updated")
                    result["rooms_inserted"] += room_stats["inserted"]
                    result["rooms_updated"] += room_stats["updated"]
                    result["rooms_skipped"] += room_stats["skipped"]

                else:
                    # LOCAL DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Local not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO local (
                            id, account_id, name, address, gps, status, enabled, 
                            default_local, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        local_id,
                        new_local_data["account_id"],
                        new_local_data["name"],
                        new_local_data["address"],
                        new_local_data["gps"],
                        new_local_data["status"],
                        new_local_data["enabled"],
                        new_local_data["default_local"],
                        new_local_data["updated_at"],  # Use updated_at as created_at
                        new_local_data["updated_at"]
                    ))
                    result["locals_inserted"] += 1
                    print(f"      ✅ Local inserted successfully")

                    # Process rooms for new local
                    room_stats = process_rooms_for_local(db, local_id, rooms, "updated")
                    result["rooms_inserted"] += room_stats["inserted"]
                    result["rooms_updated"] += room_stats["updated"]
                    result["rooms_skipped"] += room_stats["skipped"]

            except Exception as err:
                print(f"      ❌ Error processing local ID {local.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Locals: {result['locals_inserted']} inserted, "
              f"{result['locals_updated']} updated, {result['locals_skipped']} skipped | "
              f"Rooms: {result['rooms_inserted']} inserted, {result['rooms_updated']} updated, "
              f"{result['rooms_skipped']} skipped | Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_local_and_rooms: {err}")

    return result


def process_rooms_for_local(db, local_id, rooms, operation_type):
    """
    Process rooms for a specific local

    Args:
        db: Database instance
        local_id: ID of the local
        rooms: List of room data
        operation_type: "created" or "updated"

    Returns:
        dict: Room statistics
    """
    room_stats = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0
    }

    if not rooms:
        return room_stats

    print(f"      Processing {len(rooms)} room(s) for local {local_id}...")

    for room in rooms:
        try:
            room_id = room.get("id")
            if not room_id:
                continue

            # Prepare room data
            new_room_data = {
                "local_id": room.get("localId", local_id),  # Use local_id if localId not provided
                "name": room.get("name", ""),
                "capacity": room.get("capacity", ""),
                "created_at": format_date(room.get("createdAt")),
                "updated_at": format_date(room.get("updatedAt"))
            }

            # Check if room exists
            select_query = "SELECT * FROM room WHERE id = %s"
            existing_room_records = db.fetch_query(select_query, (room_id,))

            if existing_room_records:
                # ROOM EXISTS → Compare and UPDATE if different
                existing_room = existing_room_records[0]

                # Compare room data
                room_has_changes = False
                for key, value in new_room_data.items():
                    old_value = str(existing_room.get(key)) if existing_room.get(key) is not None else None
                    new_value = str(value) if value is not None else None
                    if old_value != new_value:
                        room_has_changes = True
                        break

                if not room_has_changes:
                    room_stats["skipped"] += 1
                    continue

                # Update room
                update_query = """
                    UPDATE room SET
                        local_id = %s,
                        name = %s,
                        capacity = %s,
                        created_at = %s,
                        updated_at = %s
                    WHERE id = %s
                """
                db.execute_query(update_query, (
                    new_room_data["local_id"],
                    new_room_data["name"],
                    new_room_data["capacity"],
                    new_room_data["created_at"],
                    new_room_data["updated_at"],
                    room_id
                ))
                room_stats["updated"] += 1

            else:
                # ROOM DOES NOT EXIST → INSERT
                if operation_type == "updated":
                    # For 'updated' operation, use updated_at as created_at
                    new_room_data["created_at"] = new_room_data["updated_at"]

                insert_query = """
                    INSERT INTO room (
                        id, local_id, name, capacity, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(insert_query, (
                    room_id,
                    new_room_data["local_id"],
                    new_room_data["name"],
                    new_room_data["capacity"],
                    new_room_data["created_at"],
                    new_room_data["updated_at"]
                ))
                room_stats["inserted"] += 1

        except Exception as err:
            print(f"         ❌ Error processing room ID {room.get('id', 'unknown')}: {err}")
            room_stats["errors"] += 1
            continue

    return room_stats


def process_local_and_rooms(db, local_data):
    """
    Process local and room data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        local_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING LOCALS AND ROOMS")
    print("=" * 60)

    results = {
        "created_section": {
            "locals_inserted": 0, "locals_updated": 0, "locals_skipped": 0,
            "rooms_inserted": 0, "rooms_updated": 0, "rooms_skipped": 0,
            "errors": 0
        },
        "updated_section": {
            "locals_inserted": 0, "locals_updated": 0, "locals_skipped": 0,
            "rooms_inserted": 0, "rooms_updated": 0, "rooms_skipped": 0,
            "errors": 0
        }
    }

    # Process 'created' section
    if local_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(local_data['created'])} locals)...")
        results["created_section"] = insert_local_and_rooms(db, local_data)

    # Process 'updated' section
    if local_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(local_data['updated'])} locals)...")
        results["updated_section"] = update_local_and_rooms(db, local_data)

    # Print total summary
    total_locals_inserted = results["created_section"]["locals_inserted"] + results["updated_section"]["locals_inserted"]
    total_locals_updated = results["created_section"]["locals_updated"] + results["updated_section"]["locals_updated"]
    total_locals_skipped = results["created_section"]["locals_skipped"] + results["updated_section"]["locals_skipped"]

    total_rooms_inserted = results["created_section"]["rooms_inserted"] + results["updated_section"]["rooms_inserted"]
    total_rooms_updated = results["created_section"]["rooms_updated"] + results["updated_section"]["rooms_updated"]
    total_rooms_skipped = results["created_section"]["rooms_skipped"] + results["updated_section"]["rooms_skipped"]

    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 LOCALS AND ROOMS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   LOCALS:")
    print(f"     ✨ Inserted: {total_locals_inserted}")
    print(f"     🔄 Updated:  {total_locals_updated}")
    print(f"     ⏭️  Skipped:  {total_locals_skipped}")
    print(f"   ROOMS:")
    print(f"     ✨ Inserted: {total_rooms_inserted}")
    print(f"     🔄 Updated:  {total_rooms_updated}")
    print(f"     ⏭️  Skipped:  {total_rooms_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results