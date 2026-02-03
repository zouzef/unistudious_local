"""
Account Data Processor
Handles inserting and updating account records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date
from core.auth import get_token


def download_account_image(file_link):
    """
    Download account image (placeholder - implement based on your download logic)

    Args:
        file_link: Image URL to download
    """
    try:
        if file_link:
            token = get_token()
            # TODO: Implement your image download logic here
            # from download_images.download_images_local import download_image
            # download_image(token, file_link)
            print(f"      📷 Image: {file_link}")
    except Exception as e:
        print(f"      ⚠️  Image download failed: {e}")


def insert_accounts(db, account_data):
    """
    Handle 'created' accounts from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it

    Args:
        db: Database instance
        account_data: Dictionary with 'created' key

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
        created_accounts = account_data.get("created", [])
        result["total_processed"] = len(created_accounts)

        if not created_accounts:
            print("   ℹ️  No accounts in 'created'")
            return result

        print(f"   Processing {len(created_accounts)} account(s) from 'created'...")

        for i, account in enumerate(created_accounts, 1):
            try:
                account_id = account.get("id")
                if not account_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "name": account.get("name", ""),
                    "file_link": account.get("image", ""),
                    "status": account.get("status", True),
                    "created_at": format_date(account.get("createdAt")),
                    "updated_at": format_date(account.get("updatedAt")),
                    "timestamp": format_date(account.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM account WHERE id = %s"
                existing_records = db.fetch_query(select_query, (account_id,))

                print(f"   [{i}/{len(created_accounts)}] Account ID {account_id}...")

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

                    # Download image if changed
                    if new_data["file_link"] and new_data["file_link"] != existing.get("file_link"):
                        download_account_image(new_data["file_link"])

                    update_query = """
                        UPDATE account SET
                            name = %s,
                            file_link = %s,
                            status = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["name"],
                        new_data["file_link"],
                        new_data["status"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        account_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT
                    print(f"      ✨ New record - inserting...")

                    # Download image
                    if new_data["file_link"]:
                        download_account_image(new_data["file_link"])

                    insert_query = """
                        INSERT INTO account (id, name, file_link, status, created_at, updated_at, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        account_id,
                        new_data["name"],
                        new_data["file_link"],
                        new_data["status"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account ID {account.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in insert_accounts: {err}")

    return result


def update_accounts(db, account_data):
    """
    Handle 'updated' accounts from API
    Logic:
    - If record exists in DB → UPDATE it
    - If record does NOT exist → INSERT it (don't skip!)

    Args:
        db: Database instance
        account_data: Dictionary with 'updated' key

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
        updated_accounts = account_data.get("updated", [])
        result["total_processed"] = len(updated_accounts)

        if not updated_accounts:
            print("   ℹ️  No accounts in 'updated'")
            return result

        print(f"   Processing {len(updated_accounts)} account(s) from 'updated'...")

        for i, account in enumerate(updated_accounts, 1):
            try:
                account_id = account.get("id")
                if not account_id:
                    raise ValueError("Missing required field: id")

                # Prepare new data
                new_data = {
                    "name": account.get("name", ""),
                    "file_link": account.get("image", ""),
                    "status": account.get("status", True),
                    "created_at": format_date(account.get("createdAt")),
                    "updated_at": format_date(account.get("updatedAt")),
                    "timestamp": format_date(account.get("timestamp"))
                }

                # Check if record exists
                select_query = "SELECT * FROM account WHERE id = %s"
                existing_records = db.fetch_query(select_query, (account_id,))

                print(f"   [{i}/{len(updated_accounts)}] Account ID {account_id}...")

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

                    # Download image if changed
                    if new_data["file_link"] and new_data["file_link"] != existing.get("file_link"):
                        download_account_image(new_data["file_link"])

                    update_query = """
                        UPDATE account SET
                            name = %s,
                            file_link = %s,
                            status = %s,
                            created_at = %s,
                            updated_at = %s,
                            timestamp = %s
                        WHERE id = %s
                    """

                    db.execute_query(update_query, (
                        new_data["name"],
                        new_data["file_link"],
                        new_data["status"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"],
                        account_id
                    ))

                    result["updated"] += 1
                    print(f"      ✅ Updated successfully")

                else:
                    # DOES NOT EXIST → INSERT (don't skip!)
                    print(f"      ⚠️  Record not found in DB - inserting...")

                    # Download image
                    if new_data["file_link"]:
                        download_account_image(new_data["file_link"])

                    insert_query = """
                        INSERT INTO account (id, name, file_link, status, created_at, updated_at, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                    db.execute_query(insert_query, (
                        account_id,
                        new_data["name"],
                        new_data["file_link"],
                        new_data["status"],
                        new_data["created_at"],
                        new_data["updated_at"],
                        new_data["timestamp"]
                    ))

                    result["inserted"] += 1
                    print(f"      ✅ Inserted successfully")

            except Exception as err:
                print(f"      ❌ Error processing account ID {account.get('id', 'unknown')}: {err}")
                result["errors"] += 1
                continue

        print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
              f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
              f"Errors: {result['errors']}")

    except Exception as err:
        print(f"   💥 Unexpected error in update_accounts: {err}")

    return result


def process_accounts(db, account_data):
    """
    Process account data (handles both 'created' and 'updated' sections)

    Args:
        db: Database instance
        account_data: Dictionary with 'created' and/or 'updated' keys

    Returns:
        dict: Combined statistics
    """
    print("\n📌 PROCESSING ACCOUNTS")
    print("=" * 60)

    results = {
        "created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
        "updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    }

    # Process 'created' section
    if account_data.get("created"):
        print(f"\n✨ Processing 'created' section ({len(account_data['created'])} records)...")
        results["created_section"] = insert_accounts(db, account_data)

    # Process 'updated' section
    if account_data.get("updated"):
        print(f"\n🔄 Processing 'updated' section ({len(account_data['updated'])} records)...")
        results["updated_section"] = update_accounts(db, account_data)

    # Print total summary
    total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
    total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
    total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
    total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

    print("\n" + "=" * 60)
    print("📊 ACCOUNTS - TOTAL SUMMARY")
    print("=" * 60)
    print(f"   ✨ Total Inserted: {total_inserted}")
    print(f"   🔄 Total Updated:  {total_updated}")
    print(f"   ⏭️  Total Skipped:  {total_skipped}")
    print(f"   ❌ Total Errors:   {total_errors}")
    print("=" * 60)

    return results

