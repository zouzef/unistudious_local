"""
User Data Processor
Handles inserting and updating user records in the database
"""
import sys
import os
import json

from processors.image_downloader import download_user_image, download_student_reference_images

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def normalize_roles(roles):
    """
    Normalize roles to always be a JSON array string.
    Handles both list format ["ROLE_ADMIN"] and dict format {"1": "ROLE_ADMIN", ...}
    """
    if not roles:
        return json.dumps([])
    if isinstance(roles, list):
        return json.dumps(roles)
    if isinstance(roles, dict):
        return json.dumps(list(roles.values()))
    return json.dumps([])


def insert_users(db, user_data, token):
    """
    Handle 'created' users from API
    Logic:
    - Check if id_prod already exists (avoid duplicates from local pushes)
    - If user exists in DB → UPDATE it
    - If user does NOT exist → INSERT it
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

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM user WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (user_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_users)}] User ID {user_id} already exists as id_prod "
                          f"(local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                new_data = {
                    "id_prod": user.get("userId"),
                    "uuid": user.get("uuid"),
                    "username": user.get("username", ""),
                    "full_name": user.get("fullName"),
                    "email": user.get("email", ""),
                    "phone": user.get("phone"),
                    "address": user.get("address"),
                    "roles": normalize_roles(user.get("roles")),
                    "img_link": user.get("image"),
                    "status": 1 if user.get("status") else 0,
                    "enabled": 1 if user.get("enabled", True) else 0,
                    "grand": user.get("grand"),
                    "release_token": 1 if user.get("releaseToken", False) else 0,
                    "use_token": user.get("useToken"),
                    "ref_slc": user.get("refSlc"),
                    "timestamp": format_date(user.get("timestamp")),
                    "created_at": format_date(user.get("createdAt")),
                    "updated_at": format_date(user.get("updatedAt")),
                    "isvirtual": user.get("isVirtual"),
                    "door_id": user.get("doorId"),
                    "password": user.get("password", "TEMP_PASSWORD_NEEDS_RESET"),
                }

                select_query = "SELECT * FROM user WHERE id = %s"
                existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(created_users)}] User ID {user_id}...")

                if existing_records:
                    existing = existing_records[0]

                    field_mapping = {
                        "id_prod": "id_prod",
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
                        "updated_at": "updated_at",
                        "isvirtual": "isvirtual",
                        "door_id": "door_id",
                        "password": "password",  # ✅ FIXED
                    }

                    has_changes = False
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

                    print(f"      🔄 Already exists but data changed - updating...")

                    update_query = """
                        UPDATE user SET
                            id_prod = %s,
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
                            updated_at = %s,
                            isvirtual = %s,
                            door_id = %s,
                            password = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
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
                        new_data["isvirtual"],
                        new_data["door_id"],
                        new_data["password"],  # ✅ FIXED
                        user_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                    download_user_image(user_id, new_data["img_link"], token)
                    if new_data["ref_slc"]:
                        download_student_reference_images(user_id, token)

                else:
                    print(f"      ✨ New user - inserting...")

                    default_values = {
                        "account_id": None,
                        "reset_token": None,
                        "created_by": 0,
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

                    # Columns (44 total):
                    #  1 id
                    #  2 id_prod
                    #  3 account_id
                    #  4 username
                    #  5 email
                    #  6 full_name
                    #  7 roles
                    #  8 img_link
                    #  9 reset_token
                    # 10 status
                    # 11 created_by
                    # 12 password
                    # 13 birth_date
                    # 14 birth_place
                    # 15 phone
                    # 16 address
                    # 17 grand
                    # 18 access_type
                    # 19 access_type_date
                    # 20 enabled
                    # 21 created_at
                    # 22 timestamp
                    # 23 updated_at
                    # 24 uuid
                    # 25 facebook_id
                    # 26 google_id
                    # 27 mastodon_access_token
                    # 28 general_notification
                    # 29 message_notification
                    # 30 calendar_notification
                    # 31 sms_notification
                    # 32 login_notification
                    # 33 horsline
                    # 34 ref_slc
                    # 35 apple_id
                    # 36 open_source_user_name
                    # 37 rocket_chat_user_id
                    # 38 fcm_web
                    # 39 fcm_android
                    # 40 fcm_ios
                    # 41 releaseToken
                    # 42 useToken
                    # 43 isvirtual
                    # 44 door_id
                    insert_query = """
                        INSERT INTO user (
                            id, id_prod, account_id, username, email, full_name, roles, img_link,
                            reset_token, status, created_by, password, birth_date, birth_place,
                            phone, address, grand, access_type, access_type_date, enabled,
                            created_at, timestamp, updated_at, uuid, facebook_id, google_id,
                            mastodon_access_token, general_notification, message_notification,
                            calendar_notification, sms_notification, login_notification,
                            horsline, ref_slc, apple_id, open_source_user_name,
                            rocket_chat_user_id, fcm_web, fcm_android, fcm_ios, releaseToken, useToken,
                            isvirtual, door_id
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        user_id,                                      # 1 id
                        new_data["id_prod"],                          # 2 id_prod
                        default_values["account_id"],                 # 3 account_id
                        new_data["username"],                         # 4 username
                        new_data["email"],                            # 5 email
                        new_data["full_name"],                        # 6 full_name
                        new_data["roles"],                            # 7 roles
                        new_data["img_link"],                         # 8 img_link
                        default_values["reset_token"],                # 9 reset_token
                        new_data["status"],                           # 10 status
                        default_values["created_by"],                 # 11 created_by
                        new_data["password"],                         # 12 password
                        default_values["birth_date"],                 # 13 birth_date
                        default_values["birth_place"],                # 14 birth_place
                        new_data["phone"],                            # 15 phone
                        new_data["address"],                          # 16 address
                        new_data["grand"],                            # 17 grand
                        default_values["access_type"],                # 18 access_type
                        default_values["access_type_date"],           # 19 access_type_date
                        new_data["enabled"],                          # 20 enabled
                        new_data["created_at"],                       # 21 created_at
                        new_data["timestamp"],                        # 22 timestamp
                        new_data["updated_at"],                       # 23 updated_at
                        new_data["uuid"],                             # 24 uuid
                        default_values["facebook_id"],                # 25 facebook_id
                        default_values["google_id"],                  # 26 google_id
                        default_values["mastodon_access_token"],      # 27 mastodon_access_token
                        default_values["general_notification"],       # 28 general_notification
                        default_values["message_notification"],       # 29 message_notification
                        default_values["calendar_notification"],      # 30 calendar_notification
                        default_values["sms_notification"],           # 31 sms_notification
                        default_values["login_notification"],         # 32 login_notification
                        default_values["horsline"],                   # 33 horsline
                        new_data["ref_slc"],                          # 34 ref_slc
                        default_values["apple_id"],                   # 35 apple_id
                        default_values["open_source_user_name"],      # 36 open_source_user_name
                        default_values["rocket_chat_user_id"],        # 37 rocket_chat_user_id
                        default_values["fcm_web"],                    # 38 fcm_web
                        default_values["fcm_android"],                # 39 fcm_android
                        default_values["fcm_ios"],                    # 40 fcm_ios
                        new_data["release_token"],                    # 41 releaseToken
                        new_data["use_token"],                        # 42 useToken
                        new_data["isvirtual"],                        # 43 isvirtual
                        new_data["door_id"]                           # 44 door_id
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

                    download_user_image(user_id, new_data["img_link"], token)
                    if new_data["ref_slc"]:
                        download_student_reference_images(user_id, token)

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


def update_users(db, user_data, token):
    """
    Handle 'updated' users from API
    Logic:
    - Check by id_prod first, then fall back to id
    - If user exists in DB → UPDATE it
    - If user does NOT exist → INSERT it (don't skip!)
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

                new_data = {
                    "id_prod": user.get("userId"),
                    "uuid": user.get("uuid"),
                    "username": user.get("username"),
                    "full_name": user.get("fullName"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "address": user.get("address"),
                    "roles": normalize_roles(user.get("roles")),
                    "img_link": user.get("image"),
                    "status": 1 if user.get("status") else 0,
                    "enabled": 1 if user.get("enabled", True) else 0,
                    "grand": user.get("grand"),
                    "release_token": 1 if user.get("releaseToken", False) else 0,
                    "use_token": user.get("useToken"),
                    "ref_slc": user.get("refSlc"),
                    "timestamp": format_date(user.get("timestamp")),
                    "updated_at": format_date(user.get("updatedAt")),
                    "isvirtual": user.get("isVirtual"),
                    "door_id": user.get("doorId"),
                    "password": user.get("password", "TEMP_PASSWORD_NEEDS_RESET"),
                }

                # ✅ Check by id_prod first, then fall back to id
                check_prod_query = "SELECT * FROM user WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (user_id,))

                if not existing_records:
                    select_query = "SELECT * FROM user WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(updated_users)}] User ID {user_id}...")

                if existing_records:
                    existing = existing_records[0]

                    field_mapping = {
                        "id_prod": "id_prod",
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
                        "updated_at": "updated_at",
                        "isvirtual": "isvirtual",
                        "door_id": "door_id",
                        "password": "password",  # ✅ FIXED
                    }

                    has_changes = False
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

                    print(f"      🔄 Data changed - updating...")

                    update_query = """
                        UPDATE user SET
                            id_prod = %s,
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
                            updated_at = %s,
                            isvirtual = %s,
                            door_id = %s,
                            password = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
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
                        new_data["isvirtual"],
                        new_data["door_id"],
                        new_data["password"],  # ✅ FIXED
                        existing["id"]  # ← use actual local id (handles both id and id_prod lookup)
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                    download_user_image(user_id, new_data["img_link"], token)
                    if new_data["ref_slc"]:
                        download_student_reference_images(user_id, token)

                else:
                    print(f"      ⚠️  User not found in DB - inserting...")

                    default_values = {
                        "account_id": None,
                        "reset_token": None,
                        "created_by": 0,
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
                            id, id_prod, account_id, username, email, full_name, roles, img_link,
                            reset_token, status, created_by, password, birth_date, birth_place,
                            phone, address, grand, access_type, access_type_date, enabled,
                            created_at, timestamp, updated_at, uuid, facebook_id, google_id,
                            mastodon_access_token, general_notification, message_notification,
                            calendar_notification, sms_notification, login_notification,
                            horsline, ref_slc, apple_id, open_source_user_name,
                            rocket_chat_user_id, fcm_web, fcm_android, fcm_ios, releaseToken, useToken,
                            isvirtual, door_id
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        user_id,                                      # 1 id
                        new_data["id_prod"],                          # 2 id_prod
                        default_values["account_id"],                 # 3 account_id
                        new_data["username"],                         # 4 username
                        new_data["email"],                            # 5 email
                        new_data["full_name"],                        # 6 full_name
                        new_data["roles"],                            # 7 roles
                        new_data["img_link"],                         # 8 img_link
                        default_values["reset_token"],                # 9 reset_token
                        new_data["status"],                           # 10 status
                        default_values["created_by"],                 # 11 created_by
                        new_data["password"],                         # 12 password
                        default_values["birth_date"],                 # 13 birth_date
                        default_values["birth_place"],                # 14 birth_place
                        new_data["phone"],                            # 15 phone
                        new_data["address"],                          # 16 address
                        new_data["grand"],                            # 17 grand
                        default_values["access_type"],                # 18 access_type
                        default_values["access_type_date"],           # 19 access_type_date
                        new_data["enabled"],                          # 20 enabled
                        new_data["updated_at"],                       # 21 created_at (fallback)
                        new_data["timestamp"],                        # 22 timestamp
                        new_data["updated_at"],                       # 23 updated_at
                        new_data["uuid"],                             # 24 uuid
                        default_values["facebook_id"],                # 25 facebook_id
                        default_values["google_id"],                  # 26 google_id
                        default_values["mastodon_access_token"],      # 27 mastodon_access_token
                        default_values["general_notification"],       # 28 general_notification
                        default_values["message_notification"],       # 29 message_notification
                        default_values["calendar_notification"],      # 30 calendar_notification
                        default_values["sms_notification"],           # 31 sms_notification
                        default_values["login_notification"],         # 32 login_notification
                        default_values["horsline"],                   # 33 horsline
                        new_data["ref_slc"],                          # 34 ref_slc
                        default_values["apple_id"],                   # 35 apple_id
                        default_values["open_source_user_name"],      # 36 open_source_user_name
                        default_values["rocket_chat_user_id"],        # 37 rocket_chat_user_id
                        default_values["fcm_web"],                    # 38 fcm_web
                        default_values["fcm_android"],                # 39 fcm_android
                        default_values["fcm_ios"],                    # 40 fcm_ios
                        new_data["release_token"],                    # 41 releaseToken
                        new_data["use_token"],                        # 42 useToken
                        new_data["isvirtual"],                        # 43 isvirtual
                        new_data["door_id"]                           # 44 door_id
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

                    download_user_image(user_id, new_data["img_link"], token)
                    if new_data["ref_slc"]:
                        download_student_reference_images(user_id, token)

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


def insert_admins(db, admin_data, token):
    """
    Handle admins from API → push into user table
    Logic:
    - Check if id_prod already exists (avoid duplicates from local pushes)
    - If user exists in DB → UPDATE it
    - If user does NOT exist → INSERT it

    NOTE: Admins never have reference images (no facial-recognition ref_slc
    use case for them), so download_student_reference_images is intentionally
    NOT called anywhere in this function.
    """
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        admins = admin_data.get("created", []) + admin_data.get("updated", [])
        result["total_processed"] = len(admins)

        if not admins:
            print("   ℹ️  No admins to process")
            return result

        print(f"   Processing {len(admins)} admin(s)...")

        for i, user in enumerate(admins, 1):
            try:
                user_id = user.get("userId")
                if not user_id:
                    raise ValueError("Missing required field: userId")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM user WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (user_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(admins)}] Admin ID {user_id} already exists as id_prod "
                          f"(local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                new_data = {
                    "id_prod": user.get("userId"),
                    "uuid": user.get("uuid"),
                    "username": user.get("username", ""),
                    "full_name": user.get("fullName"),
                    "email": user.get("email", ""),
                    "phone": user.get("phone"),
                    "address": user.get("address"),
                    "roles": normalize_roles(user.get("roles")),
                    "img_link": user.get("image"),
                    "status": 1 if user.get("status") else 0,
                    "enabled": 1 if user.get("enabled", True) else 0,
                    "grand": user.get("grand"),
                    "release_token": 1 if user.get("releaseToken", False) else 0,
                    "use_token": user.get("useToken"),
                    "ref_slc": user.get("refSlc"),
                    "timestamp": format_date(user.get("timestamp")),
                    "created_at": format_date(user.get("createdAt")),
                    "updated_at": format_date(user.get("updatedAt")),
                    "isvirtual": user.get("isVirtual"),
                    "door_id": user.get("doorId"),
                    "password": user.get("password", "TEMP_PASSWORD_NEEDS_RESET"),
                }

                select_query = "SELECT * FROM user WHERE id = %s"
                existing_records = db.fetch_query(select_query, (user_id,))

                print(f"   [{i}/{len(admins)}] Admin ID {user_id} ({new_data['username']})...")

                if existing_records:
                    existing = existing_records[0]

                    field_mapping = {
                        "id_prod": "id_prod",
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
                        "updated_at": "updated_at",
                        "isvirtual": "isvirtual",
                        "door_id": "door_id",
                        "password": "password",  # ✅ FIXED
                    }

                    has_changes = False
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

                    print(f"      🔄 Already exists but data changed - updating...")

                    update_query = """
                        UPDATE user SET
                            id_prod = %s,
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
                            updated_at = %s,
                            isvirtual = %s,
                            door_id = %s,
                            password = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
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
                        new_data["isvirtual"],
                        new_data["door_id"],
                        new_data["password"],  # ✅ FIXED
                        user_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                    download_user_image(user_id, new_data["img_link"], token)

                else:
                    print(f"      ✨ New admin - inserting into user table...")

                    default_values = {
                        "account_id": None,
                        "reset_token": None,
                        "created_by": 0,
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
                            id, id_prod, account_id, username, email, full_name, roles, img_link,
                            reset_token, status, created_by, password, birth_date, birth_place,
                            phone, address, grand, access_type, access_type_date, enabled,
                            created_at, timestamp, updated_at, uuid, facebook_id, google_id,
                            mastodon_access_token, general_notification, message_notification,
                            calendar_notification, sms_notification, login_notification,
                            horsline, ref_slc, apple_id, open_source_user_name,
                            rocket_chat_user_id, fcm_web, fcm_android, fcm_ios, releaseToken, useToken,
                            isvirtual, door_id
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        user_id,                                      # 1 id
                        new_data["id_prod"],                          # 2 id_prod
                        3,                                             # 3 account_id
                        new_data["username"],                         # 4 username
                        new_data["email"],                            # 5 email
                        new_data["full_name"],                        # 6 full_name
                        new_data["roles"],                            # 7 roles
                        new_data["img_link"],                         # 8 img_link
                        default_values["reset_token"],                # 9 reset_token
                        new_data["status"],                           # 10 status
                        default_values["created_by"],                 # 11 created_by
                        new_data["password"],                         # 12 password
                        default_values["birth_date"],                 # 13 birth_date
                        default_values["birth_place"],                # 14 birth_place
                        new_data["phone"],                            # 15 phone
                        new_data["address"],                          # 16 address
                        new_data["grand"],                            # 17 grand
                        default_values["access_type"],                # 18 access_type
                        default_values["access_type_date"],           # 19 access_type_date
                        new_data["enabled"],                          # 20 enabled
                        new_data["created_at"],                       # 21 created_at
                        new_data["timestamp"],                        # 22 timestamp
                        new_data["updated_at"],                       # 23 updated_at
                        new_data["uuid"],                             # 24 uuid
                        default_values["facebook_id"],                # 25 facebook_id
                        default_values["google_id"],                  # 26 google_id
                        default_values["mastodon_access_token"],      # 27 mastodon_access_token
                        default_values["general_notification"],       # 28 general_notification
                        default_values["message_notification"],       # 29 message_notification
                        default_values["calendar_notification"],      # 30 calendar_notification
                        default_values["sms_notification"],           # 31 sms_notification
                        default_values["login_notification"],         # 32 login_notification
                        default_values["horsline"],                   # 33 horsline
                        new_data["ref_slc"],                          # 34 ref_slc
                        default_values["apple_id"],                   # 35 apple_id
                        default_values["open_source_user_name"],      # 36 open_source_user_name
                        default_values["rocket_chat_user_id"],        # 37 rocket_chat_user_id
                        default_values["fcm_web"],                    # 38 fcm_web
                        default_values["fcm_android"],                # 39 fcm_android
                        default_values["fcm_ios"],                    # 40 fcm_ios
                        new_data["release_token"],                    # 41 releaseToken
                        new_data["use_token"],                        # 42 useToken
                        new_data["isvirtual"],                        # 43 isvirtual
                        new_data["door_id"]                           # 44 door_id
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

                    download_user_image(user_id, new_data["img_link"], token)

            except Exception as err:
                print(f"      ❌ Error processing admin ID {user.get('userId', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Admins section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_admins: {err}")

    return result


def process_users(db, user_data, token):
    """
    Process user data (handles both 'created' and 'updated' sections)
    """
    print("\n📌 PROCESSING USERS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if user_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(user_data['created'])} records)...")
        results["created_section"] = insert_users(db, user_data, token)

    if user_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(user_data['updated'])} records)...")
        results["updated_section"] = update_users(db, user_data, token)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
    total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
    total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 USERS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results


def process_admins(db, admin_data, token):
    """
    Process admin data and push into the user table.
    """
    print("\n📌 PROCESSING ADMINS → user table")
    print("=" * 60)

    result = insert_admins(db, admin_data, token)

    print("\n" + "=" * 60)
    print("📊 ADMINS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {result['inserted']}")
    print(f"   🔄 Total Updated:  {result['updated']}")
    print(f"   ⏭️  Total Skipped:  {result['skipped']}")
    print(f"   ❌ Total Errors:   {result['errors']}")
    print("=" * 60)

    return result