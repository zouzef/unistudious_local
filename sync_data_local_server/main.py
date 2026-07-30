"""
Reset sync state: deletes sync tracking files and drops the local database.
Run this from the sync_data_local_server directory (same place config.json lives).
"""
import os
import mysql.connector
from config.settings import get_settings


def reset_sync():
    settings = get_settings("config/config.json")

    # 1. Delete tracking files
    files_to_delete = [
        "data/sync_status.json",
        "data/sync_status.json.backup",
    ]
    for f in files_to_delete:
        if os.path.exists(f):
            os.remove(f)
            print(f"✅ Deleted: {f}")
        else:
            print(f"⚠️  Not found (skipped): {f}")

    # 2. Drop the database
    db_cfg = settings.database_config
    conn = mysql.connector.connect(
        host=db_cfg.get('host', 'localhost'),
        port=db_cfg.get('port', 3306),
        user=db_cfg.get('user'),
        password=db_cfg.get('password', ''),
    )
    cursor = conn.cursor()
    db_name = db_cfg.get('database')
    cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
    print(f"✅ Database '{db_name}' dropped.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("This will:")
    print("  - Delete data/sync_status.json")
    print("  - Delete data/sync_status.json.backup")
    print("  - Drop the 'unistudious' database")
    confirm = input("Type 'yes' to continue: ")
    if confirm == "yes":
        reset_sync()
        print("\nDone. Sync state and database have been reset.")
    else:
        print("Aborted.")