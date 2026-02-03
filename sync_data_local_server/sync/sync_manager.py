"""
Sync Manager - Orchestrates the entire synchronization process
Coordinates data fetching, processing, and status management
"""
import sys
import os
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings
from core.auth import init_auth, start_auto_refresh
from core.database import Database
from sync.data_fetcher import DataFetcher
from utils.helpers import (
    get_last_sync_time,
    save_last_sync_time,
    check_internet_connection
)


def sync_data_once(settings):
    """
    Perform one complete sync cycle

    Args:
        settings: Settings instance

    Returns:
        bool: True if sync successful, False otherwise
    """
    print("\n" + "="*60)
    print(f"🔄 STARTING SYNC AT {datetime.now()}")
    print("="*60)

    # Step 1: Check internet connection
    if not check_internet_connection(
        settings.network_check_url,
        settings.network_check_timeout
    ):
        print("❌ No internet connection. Cannot sync.")
        return False

    # Step 2: Connect to database
    db = Database(settings)
    if not db.connect():
        print("❌ Database connection failed")
        return False

    try:
        # Step 3: Get last sync time
        print("\n📅 Checking last sync time...")
        last_sync = get_last_sync_time()

        if last_sync:
            print(f"   Last sync was at: {last_sync}")
        else:
            print("   No previous sync found - performing full sync")

        # Step 4: Store current time BEFORE fetching (important!)
        sync_start_time = datetime.now()
        print(f"   Current sync started at: {sync_start_time}")

        # Step 5: Fetch data from remote server
        print("\n📡 Fetching data from remote server...")
        fetcher = DataFetcher(settings)
        data = fetcher.fetch_data(since_date=last_sync)

        # Step 6: Check if there's new data
        if not data:
            print("⚠️  No data received from server")
            return False

        if not fetcher.has_new_data(data):
            print("\nℹ️  No new data to sync. Database is up to date.")
            # Still save sync time even if no data
            save_last_sync_time(sync_start_time)
            return True

        # Step 7: Process the data
        print("\n📊 New data found! Processing...")
        process_sync_data(db, data)

        # Step 8: Save new sync time (use the time from BEFORE the API call)
        print("\n💾 Saving sync status...")
        save_last_sync_time(sync_start_time)

        print("\n" + "="*60)
        print("✅ SYNC COMPLETED SUCCESSFULLY!")
        print("="*60)
        return True

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ SYNC FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Always disconnect from database
        print("\n🔌 Closing database connection...")
        db.disconnect()


def process_sync_data(db, data):
    print("\n"+"="*60)
    print("Processing SYNC DATA ")
    print("="*60)

    if 'account' in data:
        from sync.processors.account_processor import process_accounts
        print("\n ACCOUNTS: ")
        process_accounts(db,data['account'])

    if 'accountSubject' in data:
        from sync.processors.account_subject_processor import process_account_subjects
        print("\n Account_subject: ")
        process_account_subjects(db,data['accountSubject'])

    if 'attendance' in data:
        from sync.processors.attendance_processor import process_attendances
        print("\n Attendance: ")
        process_attendances(db,data['attendance'])

    if 'calendar' in data:
        from sync.processors.calendar_processor import process_calendars
        print("\n Calendar: ")
        process_calendars(db,data['calendar'])

    if 'slcCamera' in data :
        from sync.processors.camera_processor import process_cameras
        print("\n Camera: ")
        process_cameras(db,data['slcCamera'])

    if 'formation' in data:
        from sync.processors.formation_processor import process_formations
        print("\n Formation: ")
        process_formations(db,data['formation'])

    if 'group' in data:
        from sync.processors.group_local_session_processor import process_groups
        print("\n Groups: ")
        process_groups(db,data['group'])

    if 'slcLocal' in data:
        from sync.processors.slc_local_processor import process_slc_local
        print("\n SLC local: ")
        process_slc_local(db,data['slcLocal'])

    if 'relationTeacherAndSubjectData' in data:
        from sync.processors.relation_teacher_subject_processor import process_teacher_subject_relations
        print("\n Teacher Subjects")
        process_teacher_subject_relations(db,data['relationTeacherAndSubjectData'])

    if 'relationUserSession' in data:
        from sync.processors.user_session_processor import process_user_session_relations
        print("\n Relatioon User Session: ")
        process_user_session_relations(db,data['relationUserSession'])



    if 'local_with_room' in data:
        from sync.processors.local_room_processor import process_local_and_rooms
        print("\n local_with_room")
        process_local_and_rooms(db,data['local_with_room'])

    if 'session' in data:
        from sync.processors.session_processor import process_sessions
        print("\n Session")
        process_sessions(db,data['session'])

    if 'slc' in data:
        from sync.processors.slc_processor import process_slcs
        print("\n SLC")
        process_slcs(db,data['slc'])

    if 'subject' in data:
        from sync.processors.subject_config_processor import process_subjects
        print("\n Subject: ")
        process_subjects(db,data['subject'])

    if 'slcTablet' in data:
        from sync.processors.tablet_processor import process_tablets
        print("\n SlcTablet: ")
        process_tablets(db,data['slcTablet'])

    if 'user' in data:
        from sync.processors.user_processor import process_users
        print("\n User: ")
        process_users(db,data['user'])



def run_continuous_sync(settings):
    """
    Run sync continuously at specified interval

    Args:
        settings: Settings instance
    """
    interval_minutes = settings.sync_interval_minutes

    print("\n" + "="*60)
    print("🔁 CONTINUOUS SYNC MODE")
    print("="*60)
    print(f"Sync interval: {interval_minutes} minute(s)")
    print("Press Ctrl+C to stop")
    print("="*60)

    try:
        sync_count = 0

        while True:
            sync_count += 1

            print(f"\n{'#'*60}")
            print(f"SYNC #{sync_count} - {datetime.now()}")
            print(f"{'#'*60}")

            # Perform sync
            success = sync_data_once(settings)

            if success:
                print(f"\n✅ Sync #{sync_count} completed")
            else:
                print(f"\n❌ Sync #{sync_count} failed")

            # Wait for next sync
            print(f"\n⏳ Waiting {interval_minutes} minute(s) until next sync...")
            print(f"   Next sync at: {datetime.now().replace(microsecond=0)}")

            # Sleep
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("👋 CONTINUOUS SYNC STOPPED BY USER")
        print("="*60)
        print(f"Total syncs performed: {sync_count}")


def run_sync_with_options(settings):
    """
    Interactive menu for running sync

    Args:
        settings: Settings instance
    """
    print("\n" + "="*60)
    print("🚀 SYNC MANAGER")
    print("="*60)
    print("\nChoose an option:")
    print("1. Run single sync")
    print("2. Run continuous sync")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        print("\n🚀 Running single sync...\n")
        success = sync_data_once(settings)

        if success:
            print("\n✅ Single sync completed successfully!")
        else:
            print("\n❌ Single sync failed!")
        return success

    elif choice == "2":
        run_continuous_sync(settings)
        return True

    elif choice == "3":
        print("\n👋 Goodbye!")
        return True

    else:
        print("\n❌ Invalid choice")
        return False


# Testing / Main execution
if __name__ == "__main__":
    print("="*60)
    print("🧪 SYNC MANAGER - STEP 3 TEST")
    print("="*60)

    try:
        # Load settings
        print("\n📋 Loading configuration...")
        settings = get_settings("config/config.json")

        # Initialize authentication
        print("🔐 Initializing authentication...")
        init_auth(settings)

        # Start token auto-refresh
        print("🔄 Starting token auto-refresh...")
        start_auto_refresh()

        # Give the auth system a moment to initialize
        time.sleep(1)

        # Run sync with options
        run_sync_with_options(settings)

    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()