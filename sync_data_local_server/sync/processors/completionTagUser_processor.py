"""
CompletionTagUser Data Processor
Handles inserting and updating CompletionTagUser records in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def insert_completionTagUser(db, completionTag):
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        created_records = completionTag.get("created", [])
        result["total_processed"] = len(created_records)

        if not created_records:
            print("   ℹ️  No completionTagUser records in 'created'")
            return result

        print(f"   Processing {len(created_records)} completionTagUser record(s) from 'created'...")

        for i, record in enumerate(created_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                # ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
                check_prod_query = "SELECT id FROM completion_tag_user WHERE id_prod = %s"
                existing_by_prod = db.fetch_query(check_prod_query, (record_id,))

                if existing_by_prod:
                    print(f"   [{i}/{len(created_records)}] CompletionTagUser ID {record_id} already exists as id_prod "
                          f"(local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
                    result["skipped"] += 1
                    continue

                new_data = {
                    "id_prod": record_id,
                    "user_id": record.get("userId"),
                    "tag_id": record.get("accountCompletionTagId"),
                    "session_id": record.get("sessionId"),
                    "account_id": record.get("accountId"),
                    "group_calander_id": record.get("calanderId"),
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "release_token": 1 if record.get("releaseToken", False) else 0,
                    "use_token": record.get("useToken"),
                    "timestamp": format_date(record.get("timestamp")),
                    "created_at": format_date(record.get("createdAt")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                select_query = "SELECT * FROM completion_tag_user WHERE id = %s"
                existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(created_records)}] CompletionTagUser ID {record_id}...")

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
                        UPDATE completion_tag_user SET
                            id_prod = %s,
                            user_id = %s,
                            tag_id = %s,
                            session_id = %s,
                            account_id = %s,
                            group_calander_id = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            timestamp = %s,
                            created_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["user_id"],
                        new_data["tag_id"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["group_calander_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        record_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ✨ New completionTagUser - inserting...")

                    insert_query = """
                        INSERT INTO completion_tag_user (
                            id, id_prod, user_id, tag_id, session_id, account_id,
                            group_calander_id, enabled, release_token, use_token,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["user_id"],
                        new_data["tag_id"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["group_calander_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["created_at"],
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing completionTagUser ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_completionTagUser: {err}")

    return result


def update_completionTagUser(db, completionTag):
    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "total_processed": 0
    }

    try:
        updated_records = completionTag.get("updated", [])
        result["total_processed"] = len(updated_records)

        if not updated_records:
            print("   ℹ️  No completionTagUser records in 'updated'")
            return result

        print(f"   Processing {len(updated_records)} completionTagUser record(s) from 'updated'...")

        for i, record in enumerate(updated_records, 1):
            try:
                record_id = record.get("id")
                if not record_id:
                    raise ValueError("Missing required field: id")

                new_data = {
                    "id_prod": record_id,
                    "user_id": record.get("userId"),
                    "tag_id": record.get("accountCompletionTagId"),
                    "session_id": record.get("sessionId"),
                    "account_id": record.get("accountId"),
                    "group_calander_id": record.get("calanderId"),
                    "enabled": 1 if record.get("enabled", True) else 0,
                    "release_token": 1 if record.get("releaseToken", False) else 0,
                    "use_token": record.get("useToken"),
                    "timestamp": format_date(record.get("timestamp")),
                    "updated_at": format_date(record.get("updatedAt")),
                }

                # Look up by id_prod first, then fall back to id
                check_prod_query = "SELECT * FROM completion_tag_user WHERE id_prod = %s"
                existing_records = db.fetch_query(check_prod_query, (record_id,))

                if not existing_records:
                    select_query = "SELECT * FROM completion_tag_user WHERE id = %s"
                    existing_records = db.fetch_query(select_query, (record_id,))

                print(f"   [{i}/{len(updated_records)}] CompletionTagUser ID {record_id}...")

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
                        UPDATE completion_tag_user SET
                            id_prod = %s,
                            user_id = %s,
                            tag_id = %s,
                            session_id = %s,
                            account_id = %s,
                            group_calander_id = %s,
                            enabled = %s,
                            release_token = %s,
                            use_token = %s,
                            timestamp = %s,
                            updated_at = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["id_prod"],
                        new_data["user_id"],
                        new_data["tag_id"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["group_calander_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["updated_at"],
                        existing["id"]
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    print(f"      ⚠️  CompletionTagUser not found in DB - inserting...")

                    insert_query = """
                        INSERT INTO completion_tag_user (
                            id, id_prod, user_id, tag_id, session_id, account_id,
                            group_calander_id, enabled, release_token, use_token,
                            timestamp, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """

                    db.execute_query(insert_query, (
                        record_id,
                        new_data["id_prod"],
                        new_data["user_id"],
                        new_data["tag_id"],
                        new_data["session_id"],
                        new_data["account_id"],
                        new_data["group_calander_id"],
                        new_data["enabled"],
                        new_data["release_token"],
                        new_data["use_token"],
                        new_data["timestamp"],
                        new_data["updated_at"],  # used as created_at too
                        new_data["updated_at"],
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing completionTagUser ID {record.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_completionTagUser: {err}")

    return result


def process_completionTaguser(db, completionTag):
    """
    Process completionTagUser data (handles both 'created' and 'updated' sections)
    """
    print("\n📌 PROCESSING COMPLETION TAG USER")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    if completionTag.get("created"):
        print(f"\n✨ Processing 'created' section ({len(completionTag['created'])} record(s))...")
        results["created_section"] = insert_completionTagUser(db, completionTag)

    if completionTag.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(completionTag['updated'])} record(s))...")
        results["updated_section"] = update_completionTagUser(db, completionTag)

    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 RELATION COMPLETION TAG - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results