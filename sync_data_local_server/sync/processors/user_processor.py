"""
User Data Processor
Handles inserting and updating user records in the database
"""
import sys
import os
import json

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date



def insert_users(db, user_data):
    """
    Handle 'created' users from API
    Logic:
    - If user exists in DB → UPDATE it
    - If user does NOT exist → INSERT it

    Args:
        db: Database instance
        user_data: Dictionary with 'created' key

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
        created_users = user_data.get("created", [])
        result["total_processed"] = len(created_users)

        if not created_users:
            print("   ℹ️  No users in 'created'")
            return result

        print(f"   Processing {len(created_users)} user(s) from 'created'...")

        for i, user in enumerate(created_users, 1):
            try:
                user_id = user.get("userId")
                if not user_id:
                    raise ValueError("Missing required field: userId")

                # Prepare new data
                new_data = {
                    "uuid": user.get("uuid"),
                    "username": user.get("username", ""),
                    "full_name": user.get("fullName"),
                    "email": user.get("email", ""),
                    "phone": user.get("phone"),
                    "address": user.get("address"),
                    "roles": json.dumps(user.get("roles", [])) if user.get("roles") else json.dumps([]),
                    "img_link": user.get("image"),
                    "status": 1 if user.get("status") else 0,
                    "enabled": 1 if user.get("enabled", True) else 0,
                    "grand": user.get("grand"),
                    "release_token": 1 if user.get("releaseToken", False) else 0,
                    "use_token": user.get("useToken"),
                    "ref_slc": user.get("refSlc"),
                    "timestamp": format_date(user.get("timestamp")),
                    "created_at": format_date(user.get("createdAt")),
                    "updated_at": format_date(user.get("updatedAt"))
                }

                # Check if user exists
                select_query = "SELECT * FROM user WHERE id = %s"
                existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(created_users)}] User ID {user_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data (only compare fields we have in new_data)
                    has_changes = False
                    comparison_fields = ["username", "full_name", "email", "phone", "address",
                                         "roles", "img_link", "status", "enabled", "grand",
                                         "releaseToken", "useToken", "ref_slc", "timestamp",
                                         "updated_at"]

                    # Map our new_data keys to database column names
                    field_mapping = {
                        "username": "username",
                        "full_name": "full_name",
                        "email": "email",
                        "phone": "phone",
                        "address": "address",
                        "roles": "roles",
                        "img_link": "img_link",
                        "status": "status",
                        "enabled": "enabled",
                        "grand": "grand",
                        "release_token": "releaseToken",
                        "use_token": "useToken",
                        "ref_slc": "ref_slc",
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
                        print(f"      ⏭️  Already exists with same data - skipped")
                        result["skipped"] += 1
                        continue

                    # Data is different - UPDATE
                    print(f"      🔄 Already exists but data changed - updating...")

                    update_query = """
                        UPDATE user SET
                            username = %s,
                            full_name = %s,
                            email = %s,
                            phone = %s,
                            address = %s,
                            roles = %s,
                            img_link = %s,
                            status = %s,
                            enabled = %s,
                            grand = %s,
                            releaseToken = %s,
                            useToken = %s,
                            ref_slc = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["username"],
                        new_data["full_name"],
                        new_data["email"],
                        new_data["phone"],
                        new_data["address"],
                        new_data["roles"],
                        new_data["img_link"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["grand"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["ref_slc"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        user_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New user - inserting...")

                    # Default static fields
                    default_values = {
                        "account_id": None,
                        "reset_token": None,
                        "created_by": 0,
                        "password": "TEMP_PASSWORD_NEEDS_RESET",
                        "birth_date": None,
                        "birth_place": None,
                        "access_type": None,
                        "access_type_date": None,
                        "facebook_id": None,
                        "google_id": None,
                        "mastodon_access_token": None,
                        "general_notification": 1,
                        "message_notification": 1,
                        "calendar_notification": 1,
                        "sms_notification": 1,
                        "login_notification": 1,
                        "horsline": 0,
                        "apple_id": None,
                        "open_source_user_name": None,
                        "rocket_chat_user_id": None,
                        "fcm_web": None,
                        "fcm_android": None,
                        "fcm_ios": None
                    }

                    insert_query = """
                        INSERT INTO user (
                            id, account_id, username, email, full_name, roles, img_link,
                            reset_token, status, created_by, password, birth_date, birth_place,
                            phone, address, grand, access_type, access_type_date, enabled,
                            created_at, timestamp, updated_at, uuid, facebook_id, google_id,
                            mastodon_access_token, general_notification, message_notification,
                            calendar_notification, sms_notification, login_notification,
                            horsline, ref_slc, apple_id, open_source_user_name,
                            rocket_chat_user_id, fcm_web, fcm_android, fcm_ios, releaseToken, useToken
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        user_id,
                        default_values["account_id"],
                        new_data["username"],
                        new_data["email"],
                        new_data["full_name"],
                        new_data["roles"],
                        new_data["img_link"],
                        default_values["reset_token"],
                        new_data["status"],
                        default_values["created_by"],
                        default_values["password"],
                        default_values["birth_date"],
                        default_values["birth_place"],
                        new_data["phone"],
                        new_data["address"],
                        new_data["grand"],
                        default_values["access_type"],
                        default_values["access_type_date"],
                        new_data["enabled"],
                        new_data["created_at"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        new_data["uuid"],
                        default_values["facebook_id"],
                        default_values["google_id"],
                        default_values["mastodon_access_token"],
                        default_values["general_notification"],
                        default_values["message_notification"],
                        default_values["calendar_notification"],
                        default_values["sms_notification"],
                        default_values["login_notification"],
                        default_values["horsline"],
                        new_data["ref_slc"],
                        default_values["apple_id"],
                        default_values["open_source_user_name"],
                        default_values["rocket_chat_user_id"],
                        default_values["fcm_web"],
                        default_values["fcm_android"],
                        default_values["fcm_ios"],
                        new_data["release_token"],
                        new_data["use_token"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

                    # Download missing reference images
                    try:
                        get_student_references(user_id)
                        print(f"      📷 Downloaded images for user {user_id}")
                    except Exception as e:
                        print(f"      ⚠️  Could not download images for user {user_id}: {e}")

            except Exception as err:
                print(f"      ❌ Error processing user ID {user.get('userId', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_users: {err}")

    return result


def update_users(db, user_data):
    """
    Handle 'updated' users from API
    Logic:
    - If user exists in DB → UPDATE it
    - If user does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        user_data: Dictionary with 'updated' key

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
        updated_users = user_data.get("updated", [])
        result["total_processed"] = len(updated_users)

        if not updated_users:
            print("   ℹ️  No users in 'updated'")
            return result

        print(f"   Processing {len(updated_users)} user(s) from 'updated'...")

        for i, user in enumerate(updated_users, 1):
            try:
                user_id = user.get("userId")
                if not user_id:
                    raise ValueError("Missing required field: userId")

                # Prepare new data
                new_data = {
                    "uuid": user.get("uuid"),
                    "username": user.get("username"),
                    "full_name": user.get("fullName"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "address": user.get("address"),
                    "roles": json.dumps(user.get("roles", [])) if user.get("roles") else json.dumps([]),
                    "img_link": user.get("image"),
                    "status": 1 if user.get("status") else 0,
                    "enabled": 1 if user.get("enabled", True) else 0,
                    "grand": user.get("grand"),
                    "release_token": 1 if user.get("releaseToken", False) else 0,
                    "use_token": user.get("useToken"),
                    "ref_slc": user.get("refSlc"),
                    "timestamp": format_date(user.get("timestamp")),
                    "updated_at": format_date(user.get("updatedAt"))
                }

                # Check if user exists
                select_query = "SELECT * FROM user WHERE id = %s"
                existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(updated_users)}] User ID {user_id}...")

                if existing_records:
                    # EXISTS → Compare and UPDATE if different
                    existing = existing_records[0]

                    # Compare data
                    has_changes = False
                    comparison_fields = ["username", "full_name", "email", "phone", "address",
                                         "roles", "img_link", "status", "enabled", "grand",
                                         "releaseToken", "useToken", "ref_slc", "timestamp",
                                         "updated_at"]

                    field_mapping = {
                        "username": "username",
                        "full_name": "full_name",
                        "email": "email",
                        "phone": "phone",
                        "address": "address",
                        "roles": "roles",
                        "img_link": "img_link",
                        "status": "status",
                        "enabled": "enabled",
                        "grand": "grand",
                        "release_token": "releaseToken",
                        "use_token": "useToken",
                        "ref_slc": "ref_slc",
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
                        UPDATE user SET
                            username = %s,
                            full_name = %s,
                            email = %s,
                            phone = %s,
                            address = %s,
                            roles = %s,
                            img_link = %s,
                            status = %s,
                            enabled = %s,
                            grand = %s,
                            releaseToken = %s,
                            useToken = %s,
                            ref_slc = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["username"],
                        new_data["full_name"],
                        new_data["email"],
                        new_data["phone"],
                        new_data["address"],
                        new_data["roles"],
                        new_data["img_link"],
                        new_data["status"],
                        new_data["enabled"],
                        new_data["grand"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["ref_slc"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        user_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  User not found in DB - inserting...")

                    # Default static fields
                    default_values = {
                        "account_id": None,
                        "reset_token": None,
                        "created_by": 0,
                        "password": "TEMP_PASSWORD_NEEDS_RESET",
                        "birth_date": None,
                        "birth_place": None,
                        "access_type": None,
                        "access_type_date": None,
                        "facebook_id": None,
                        "google_id": None,
                        "mastodon_access_token": None,
                        "general_notification": 1,
                        "message_notification": 1,
                        "calendar_notification": 1,
                        "sms_notification": 1,
                        "login_notification": 1,
                        "horsline": 0,
                        "apple_id": None,
                        "open_source_user_name": None,
                        "rocket_chat_user_id": None,
                        "fcm_web": None,
                        "fcm_android": None,
                        "fcm_ios": None
                    }

                    insert_query = """
                        INSERT INTO user (
                            id, account_id, username, email, full_name, roles, img_link,
                            reset_token, status, created_by, password, birth_date, birth_place,
                            phone, address, grand, access_type, access_type_date, enabled,
                            created_at, timestamp, updated_at, uuid, facebook_id, google_id,
                            mastodon_access_token, general_notification, message_notification,
                            calendar_notification, sms_notification, login_notification,
                            horsline, ref_slc, apple_id, open_source_user_name,
                            rocket_chat_user_id, fcm_web, fcm_android, fcm_ios, releaseToken, useToken
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                    """

                    # For records in 'updated' that don't exist, use updated_at as created_at
                    db.execute_query(insert_query, (
                        user_id,
                        default_values["account_id"],
                        new_data["username"],
                        new_data["email"],
                        new_data["full_name"],
                        new_data["roles"],
                        new_data["img_link"],
                        default_values["reset_token"],
                        new_data["status"],
                        default_values["created_by"],
                        default_values["password"],
                        default_values["birth_date"],
                        default_values["birth_place"],
                        new_data["phone"],
                        new_data["address"],
                        new_data["grand"],
                        default_values["access_type"],
                        default_values["access_type_date"],
                        new_data["enabled"],
                        new_data["updated_at"],  # Use updated_at as created_at
                        new_data["timestamp"],
                        new_data["updated_at"],
                        new_data["uuid"],
                        default_values["facebook_id"],
                        default_values["google_id"],
                        default_values["mastodon_access_token"],
                        default_values["general_notification"],
                        default_values["message_notification"],
                        default_values["calendar_notification"],
                        default_values["sms_notification"],
                        default_values["login_notification"],
                        default_values["horsline"],
                        new_data["ref_slc"],
                        default_values["apple_id"],
                        default_values["open_source_user_name"],
                        default_values["rocket_chat_user_id"],
                        default_values["fcm_web"],
                        default_values["fcm_android"],
                        default_values["fcm_ios"],
                        new_data["release_token"],
                        new_data["use_token"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

                    # Download missing reference images
                    try:
                        get_student_references(user_id)
                        print(f"      📷 Downloaded images for user {user_id}")
                    except Exception as e:
                        print(f"      ⚠️  Could not download images for user {user_id}: {e}")

            except Exception as err:
                print(f"      ❌ Error processing user ID {user.get('userId', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_users: {err}")

    return result


def process_users(db, user_data):
    """
    Process user data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        user_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING USERS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if user_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(user_data['created'])} records)...")
        results["created_section"] = insert_users(db, user_data)

    # Process 'updated' section
    if user_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(user_data['updated'])} records)...")
        results["updated_section"] = update_users(db, user_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 USERS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results