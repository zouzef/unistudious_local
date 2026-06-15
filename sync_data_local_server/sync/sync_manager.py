"""
Sync Manager - Orchestrates the entire synchronization process
Coordinates data fetching, processing, and status management
"""
import sys
import os
import logging
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings
from core.auth import init_auth, start_auto_refresh
from core.database import Database
from core.database_initializer import init_database
from sync.data_fetcher import DataFetcher
from utils.helpers import (
    get_last_sync_time,
    save_last_sync_time,
    check_internet_connection
)
from sync.data_pusher import DataPusher

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def setup_logging(log_level=logging.DEBUG, log_file=None):
    """
    Configure the root logger with a console handler and an optional file handler.

    Args:
        log_level: Logging level (default DEBUG).
        log_file:  Optional path to a log file. When provided, logs are written
                   to both the console and that file.
    """
    fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(level=log_level, format=fmt, datefmt=datefmt, handlers=handlers)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def sync_data_once(settings):
    """
    Perform one complete sync cycle.

    Returns:
        bool: True if sync successful, False otherwise.
    """
    logger.info("=" * 60)
    logger.info("STARTING SYNC AT %s", datetime.now())
    logger.info("=" * 60)

    # Step 1: Check internet connection
    if not check_internet_connection(
        settings.network_check_url,
        settings.network_check_timeout
    ):
        logger.error("No internet connection. Cannot sync.")
        return False

    # Step 2: Connect to database
    db = Database(settings)
    if not db.connect():
        logger.error("Database connection failed.")
        return False

    try:
        # Step 3: Get last sync time
        logger.info("Checking last sync time...")
        last_sync = get_last_sync_time()

        if last_sync:
            logger.info("Last sync was at: %s", last_sync)
        else:
            logger.info("No previous sync found - performing full sync.")

        # Step 4: Store current time BEFORE fetching (important!)
        sync_start_time = datetime.now() - timedelta(hours=1)
        logger.debug("Current sync started at: %s", sync_start_time)

        # Step 5: Fetch data from remote server
        logger.info("Fetching data from remote server...")
        fetcher = DataFetcher(settings)
        data = fetcher.fetch_data(since_date=last_sync)

        # Step 6: Check if there's new data
        if not data:
            logger.warning("No data received from server.")
            return False

        if not fetcher.has_new_data(data):
            logger.info("No new data to sync. Database is up to date.")
            pusher = DataPusher(settings)
            pusher.detect_and_push_local_changes(db)
            save_last_sync_time(sync_start_time)
            return True

        # Step 7: Process the data
        logger.info("New data found! Processing...")
        process_sync_data(db, data, settings)

        logger.info("Pushing local changes to remote...")
        pusher = DataPusher(settings)
        pusher.detect_and_push_local_changes(db)

        # Step 8: Save new sync time
        logger.info("Saving sync status...")
        save_last_sync_time(sync_start_time)

        logger.info("=" * 60)
        logger.info("SYNC COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.exception("SYNC FAILED: %s", e)
        return False

    finally:
        logger.debug("Closing database connection...")
        db.disconnect()


def process_sync_data(db, data, settings):
    logger.info("=" * 60)
    logger.info("Processing SYNC DATA")
    logger.info("=" * 60)

    from core.auth import get_token
    token = get_token()

    def normalize(raw):
        if isinstance(raw, list):
            return {"created": raw}
        return raw

    def has_records(normalized):
        """Return True only if the normalized dict has at least one non-empty list."""
        return any(
            isinstance(v, list) and len(v) > 0
            for v in normalized.values()
        )

    if 'account' in data:
        n = normalize(data['account'])
        if has_records(n):
            from sync.processors.account_processor import process_accounts
            logger.info("Processing ACCOUNTS...")
            process_accounts(db, n, token)

    if 'accountSubject' in data:
        n = normalize(data['accountSubject'])
        if has_records(n):
            from sync.processors.account_subject_processor import process_account_subjects
            logger.info("Processing Account Subjects...")
            process_account_subjects(db, n)

    if 'calendar' in data:
        n = normalize(data['calendar'])
        if has_records(n):
            from sync.processors.calendar_processor import process_calendars
            logger.info("Processing Calendars...")
            process_calendars(db, n)

    if 'group' in data:
        n = normalize(data['group'])
        if has_records(n):
            from sync.processors.group_local_session_processor import process_groups
            logger.info("Processing Groups...")
            process_groups(db, n)

    if 'attendance' in data:
        n = normalize(data['attendance'])
        if has_records(n):
            from sync.processors.attendance_processor import process_attendances
            logger.info("Processing Attendances...")
            process_attendances(db, n, settings)

    if 'slcCamera' in data:
        n = normalize(data['slcCamera'])
        if has_records(n):
            from sync.processors.camera_processor import process_cameras
            logger.info("Processing Cameras...")
            process_cameras(db, n)

    if 'formation' in data:
        n = normalize(data['formation'])
        if has_records(n):
            from sync.processors.formation_processor import process_formations
            logger.info("Processing Formations...")
            process_formations(db, n)

    if 'slcLocal' in data:
        n = normalize(data['slcLocal'])
        if has_records(n):
            from sync.processors.slc_local_processor import process_slc_local
            logger.info("Processing SLC Locals...")
            process_slc_local(db, n)

    if 'relationTeacherAndSubjectData' in data:
        n = normalize(data['relationTeacherAndSubjectData'])
        if has_records(n):
            from sync.processors.relation_teacher_subject_processor import process_teacher_subject_relations
            logger.info("Processing Teacher-Subject Relations...")
            process_teacher_subject_relations(db, n)

    if 'relationUserSession' in data:
        n = normalize(data['relationUserSession'])
        if has_records(n):
            from sync.processors.user_session_processor import process_user_session_relations
            logger.info("Processing User-Session Relations...")
            process_user_session_relations(db, n)

    if 'local_with_room' in data:
        n = normalize(data['local_with_room'])
        if has_records(n):
            from sync.processors.local_room_processor import process_local_and_rooms
            logger.info("Processing Locals and Rooms...")
            process_local_and_rooms(db, n)

    if 'session' in data:
        n = normalize(data['session'])
        if has_records(n):
            from sync.processors.session_processor import process_sessions
            logger.info("Processing Sessions...")
            process_sessions(db, n, token)

    if 'slc' in data:
        n = normalize(data['slc'])
        if has_records(n):
            from sync.processors.slc_processor import process_slcs
            logger.info("Processing SLCs...")
            process_slcs(db, n)

    if 'subject' in data:
        n = normalize(data['subject'])
        if has_records(n):
            from sync.processors.subject_config_processor import process_subjects
            logger.info("Processing Subjects...")
            process_subjects(db, n)

    if 'slcTablet' in data:
        n = normalize(data['slcTablet'])
        if has_records(n):
            from sync.processors.tablet_processor import process_tablets
            logger.info("Processing Tablets...")
            process_tablets(db, n)

    if 'user' in data:
        n = normalize(data['user'])
        if has_records(n):
            from sync.processors.user_processor import process_users
            logger.info("Processing Users...")
            process_users(db, n, token)

    if 'admin' in data:
        n = normalize(data['admin'])
        if has_records(n):
            from sync.processors.user_processor import process_admins
            logger.info("Processing Admins...")
            process_admins(db, n, token)

    if 'virtualUser' in data:
        n = normalize(data['virtualUser'])
        if has_records(n):
            from sync.processors.VirtuelUser_processor import process_virtuelUser
            logger.info("Processing Virtual Users...")
            process_virtuelUser(db, n, token)

    if 'paymentSessions' in data:
        n = normalize(data['paymentSessions'])
        if has_records(n):
            from sync.processors.payment_processor import process_payment_sessions
            logger.info("Processing Payment Sessions...")
            process_payment_sessions(db, n)

    if 'invoices' in data:
        n = normalize(data['invoices'])
        if has_records(n):
            from sync.processors.invoice_processor import process_invoice_session
            logger.info("Processing Invoices...")
            process_invoice_session(db, n)

    if 'level' in data:
        n = normalize(data['level'])
        if has_records(n):
            from sync.processors.level_processor import processor_level_session
            logger.info("Processing Levels...")
            processor_level_session(db, n)

    if 'accountLevel' in data:
        n = normalize(data['accountLevel'])
        if has_records(n):
            from sync.processors.accountLevel_processor import processor_account_level
            logger.info("Processing Account Levels...")
            processor_account_level(db, n)

    if 'section' in data:
        n = normalize(data['section'])
        if has_records(n):
            from sync.processors.section_processor import processor_section
            logger.info("Processing Sections...")
            processor_section(db, n)

    if 'accountSection' in data:
        n = normalize(data['accountSection'])
        if has_records(n):
            from sync.processors.account_section_processor import processor_account_section
            logger.info("Processing Account Sections...")
            processor_account_section(db, n)

    if 'tag' in data:
        n = normalize(data['tag'])
        if has_records(n):
            from sync.processors.tag_config_processor import processor_tag_config
            logger.info("Processing Tag Configs...")
            processor_tag_config(db, n)

    if 'accountTag' in data:
        n = normalize(data['accountTag'])
        if has_records(n):
            from sync.processors.account_tag_processor import processor_account_tag
            logger.info("Processing Account Tags...")
            processor_account_tag(db, n)

    if 'completionTagAccount' in data:
        n = normalize(data['completionTagAccount'])
        if has_records(n):
            from sync.processors.completion_tag_account_processor import processor_completion_tag
            logger.info("Processing Completion Tags...")
            processor_completion_tag(db, n)

    if 'season' in data:
        n = normalize(data['season'])
        if has_records(n):
            from sync.processors.season_processor import process_season
            logger.info("Processing Season ...")
            process_season(db,n)

    if 'seasonSubSubject' in data:
        n = normalize(data['seasonSubSubject'])
        if has_records(n):
            from sync.processors.subsubject_processor import process_subsubject
            logger.info("Processing Subsubject")
            process_subsubject(db,n)



# ---------------------------------------------------------------------------
# Sync runners
# ---------------------------------------------------------------------------

def run_continuous_sync(settings):
    """Run sync continuously at the interval defined in settings."""
    interval_minutes = settings.sync_interval_minutes

    logger.info("=" * 60)
    logger.info("CONTINUOUS SYNC MODE")
    logger.info("Sync interval: %d minute(s) | Press Ctrl+C to stop", interval_minutes)
    logger.info("=" * 60)

    sync_count = 0
    try:
        while True:
            sync_count += 1
            logger.info("#" * 60)
            logger.info("SYNC #%d - %s", sync_count, datetime.now())
            logger.info("#" * 60)

            success = sync_data_once(settings)

            if success:
                logger.info("Sync #%d completed successfully.", sync_count)
            else:
                logger.error("Sync #%d failed.", sync_count)

            logger.info(
                "Waiting %d minute(s) until next sync (next at %s)...",
                interval_minutes,
                datetime.now().replace(microsecond=0),
            )
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("CONTINUOUS SYNC STOPPED BY USER. Total syncs: %d", sync_count)
        logger.info("=" * 60)


def run_sync_with_options(settings):
    """Interactive menu for running sync."""
    logger.info("=" * 60)
    logger.info("SYNC MANAGER")
    logger.info("=" * 60)

    print("\nChoose an option:")
    print("1. Run single sync")
    print("2. Run continuous sync")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        logger.info("Running single sync...")
        success = sync_data_once(settings)
        if success:
            logger.info("Single sync completed successfully.")
        else:
            logger.error("Single sync failed.")
        return success

    elif choice == "2":
        run_continuous_sync(settings)
        return True

    elif choice == "3":
        logger.info("Exiting.")
        return True

    else:
        logger.warning("Invalid menu choice: %s", choice)
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Configure logging before anything else.
    # Change log_file path or log_level here as needed.
    setup_logging(
        log_level=logging.DEBUG,
        log_file="logs/sync_manager.log",   # set to None to disable file logging
    )

    logger.info("=" * 60)
    logger.info("SYNC MANAGER - STARTING")
    logger.info("=" * 60)

    try:
        logger.info("Loading configuration...")
        settings = get_settings("config/config.json")

        init_database(settings)

        logger.info("Initializing authentication...")
        init_auth(settings)

        logger.info("Starting token auto-refresh...")
        start_auto_refresh()

        time.sleep(1)

        run_continuous_sync(settings)

    except KeyboardInterrupt:
        logger.info("Stopped by user.")

    except Exception as e:
        logger.exception("Unhandled error: %s", e)