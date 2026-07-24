"""
VirtualUser Data Processor
Handles inserting and updating virtual_user records in the database
"""
import sys
import os
import json

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def serialize_data(value):
    """Convert list/dict to JSON string for DB storage, leave None as None."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


def insert_virtuelUsers(db, virtualUser_data):
    """
    Handle 'created' VirtualUsers from API
    Logic:
    - If this remote ID already exists as id_prod (pushed from local) → SKIP (avoid duplicate)
    - If VirtualUser exists in DB by local id → UPDATE it
    - If VirtualUser does NOT exist → INSERT it

    Args:
        db: Database instance
        virtualUser_data: Dictionary with 'created' key

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
        created_users = virtualUser_data.get("created", [])
        result["total_processed"] = len(created_users)

        if not created_users:
            print("   ℹ️  No VirtualUsers in 'created'")
            return result

        print(f"   Processing {len(created_users)} VirtualUser(s) from 'created'...")

        for i, user in enumerate(created_users, 1):
            try:
                user_id = user.get("id")
                if not user_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM virtual_user WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (user_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_users)}] VirtualUser ID {user_id} already exists as id_prod "
                          f"(local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                # Prepare new data
                # NOTE: this section handles brand-new/incoming records, so user_id
                # and created_at are kept here (needed for INSERT).
                new_data = {
                    "id_prod": user.get("id"),
                    "account_id": user.get("accountId"),
                    "user_id": user.get("userId"),
                    "created_by_id": user.get("createdById"),
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "data": serialize_data(user.get("data")),
                    "status": int(user.get("status")) if user.get("status") is not None else None,
                    "enabled": int(user.get("enabled")) if user.get("enabled") is not None else None,
                    "release_token": int(user.get("releaseToken")) if user.get("releaseToken") is not None else 0,
                    "use_token": user.get("useToken"),
                    "uuid": user.get("uuid"),
                    "timestamp": format_date(user.get("timestamp")),
                    "created_at": format_date(user.get("createdAt")),
                    "updated_at": format_date(user.get("updatedAt")),
                }

                # Check if VirtualUser exists by local id
                select_query = "SELECT * FROM virtual_user WHERE id = %s"
                existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(created_users)}] VirtualUser ID {user_id}...")

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
                        UPDATE virtual_user SET
                            id_prod = %s,
                            account_id = %s,
                            user_id = %s,
                            created_by_id = %s,
                            name = %s,
                            email = %s,
                            phone = %s,
                            data = %s,
                            status = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            uuid = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["created_by_id"],
                        new_data["name"],
                        new_data["email"],
                        new_data["phone"],
                        new_data["data"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["uuid"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        existing["id"]
                    ))
                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New VirtualUser - inserting...")

                    insert_query = """
                        INSERT INTO virtual_user (
                            id, id_prod, account_id, user_id, created_by_id, name, email, phone,
                            data, status, enabled, release_token, use_token,
                            uuid, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        user_id,
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["user_id"],
                        new_data["created_by_id"],
                        new_data["name"],
                        new_data["email"],
                        new_data["phone"],
                        new_data["data"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["uuid"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing VirtualUser ID {user.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_virtuelUsers: {err}")

    return result


def update_virtuelUsers(db, virtualUser_data):
    """
    Handle 'updated' VirtualUsers from API
    Logic:
    - Look up by id_prod first, then fall back to local id
    - If VirtualUser exists in DB → UPDATE it (user_id is NEVER touched on update)
    - If VirtualUser does NOT exist → INSERT it (don't skip! user_id is set here since it's a new row)

    Args:
        db: Database instance
        virtualUser_data: Dictionary with 'updated' key

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
        updated_users = virtualUser_data.get("updated", [])
        result["total_processed"] = len(updated_users)

        if not updated_users:
            print("   ℹ️  No VirtualUsers in 'updated'")
            return result

        print(f"   Processing {len(updated_users)} VirtualUser(s) from 'updated'...")

        for i, user in enumerate(updated_users, 1):
            try:
                user_id = user.get("id")
                if not user_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data for the UPDATE path.
                # NOTE: user_id intentionally excluded here - on update we never
                # want to touch the user_id column, so it's left out of both the
                # change-comparison and the UPDATE query/params below.
                new_data = {
                    "id_prod": user.get("id"),
                    "account_id": user.get("accountId"),
                    "created_by_id": user.get("createdById"),
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "data": serialize_data(user.get("data")),
                    "status": int(user.get("status")) if user.get("status") is not None else None,
                    "enabled": int(user.get("enabled")) if user.get("enabled") is not None else None,
                    "release_token": int(user.get("releaseToken")) if user.get("releaseToken") is not None else 0,
                    "use_token": user.get("useToken"),
                    "uuid": user.get("uuid"),
                    "timestamp": format_date(user.get("timestamp")),
                    "updated_at": format_date(user.get("updatedAt")),
                }

                # Look up by id_prod first, then fall back to id
                check_prod_query = "SELECT * FROM virtual_user WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (user_id,))

                if not existing_records:
                    select_query = "SELECT * FROM virtual_user WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(updated_users)}] VirtualUser ID {user_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different (user_id excluded from both)
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

                    # Data is different - UPDATE (user_id column NOT included)
                    print(f"      🔄 Data changed - updating...")

                    update_query = """
                        UPDATE virtual_user SET
                            id_prod = %s,
                            account_id = %s,
                            created_by_id = %s,
                            name = %s,
                            email = %s,
                            phone = %s,
                            data = %s,
                            status = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            uuid = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["account_id"],
                        new_data["created_by_id"],
                        new_data["name"],
                        new_data["email"],
                        new_data["phone"],
                        new_data["data"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["uuid"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    # This is a brand-new row, so user_id IS required here -
                    # pulled fresh from the payload since it wasn't kept in new_data above.
                    print(f"      ⚠️  VirtualUser not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO virtual_user (
                            id, id_prod, account_id, user_id, created_by_id, name, email, phone,
                            data, status, enabled, release_token, use_token,
                            uuid, timestamp, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        user_id,
                        new_data["id_prod"],
                        new_data["account_id"],
                        user.get("userId"),
                        new_data["created_by_id"],
                        new_data["name"],
                        new_data["email"],
                        new_data["phone"],
                        new_data["data"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["uuid"],
                        new_data["timestamp"],
                        new_data["updated_at"],   # Use updated_at as created_at
                        new_data["updated_at"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing VirtualUser ID {user.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_virtuelUsers: {err}")

    return result


def process_virtuelUser(db, virtualUser_data, token=None):
    """
    Process VirtualUser data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        virtualUser_data: Dictionary with 'created' and/or 'updated' keys
        token: Optional token (reserved for future use)

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING VIRTUAL USERS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if virtualUser_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(virtualUser_data['created'])} records)...")
        results["created_section"] = insert_virtuelUsers(db, virtualUser_data)

    # Process 'updated' section
    if virtualUser_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(virtualUser_data['updated'])} records)...")
        results["updated_section"] = update_virtuelUsers(db, virtualUser_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 VIRTUAL USERS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results