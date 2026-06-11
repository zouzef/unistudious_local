import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync.pushers.attendance_pusher import push_add, push_update, send_new_attendance
from sync.pushers.calendar_pusher import push_calendar_add, push_calendar_update, push_calendar_delete
from sync.pushers.accountLevel_pusher import push_accountLevelAdd,push_accountLevelUpdate,push_accountLevelDelete
from sync.pushers.accountSection_pusher import push_accountSectionAdd, push_accountSectionUpdate,push_accountSectionDelete
from sync.pushers.accountSubject_pusher import push_accountSubjectAdd, push_accountSubjectUpdate, push_accountSubjectDelete
from sync.pushers.accountTag_pusher import push_accountTagAdd, push_accountTagUpdate, push_accountTagDelte
logger = logging.getLogger(__name__)


class DataPusher:

    def __init__(self, settings):
        self.settings = settings

    def _process_audit_rows(self, cursor, conn, table_name, rows, action_handlers):
        for row in rows:
            audit_id = row['audit_id']
            action = row['action_type']

            logger.debug("Processing %s audit #%s | action = %s", table_name, audit_id, action)

            handler = action_handlers.get(action)

            if not handler:
                logger.warning("Unknown action: %s in %s audit #%s — skipping", action, table_name, audit_id)
                continue

            success = handler(row)

            if success:
                cursor.execute(f"""
                    UPDATE {table_name} 
                    SET is_synced = 1 
                    WHERE audit_id = %s
                """, (audit_id,))
                conn.commit()
                logger.info("%s audit #%s marked as synced", table_name, audit_id)
            else:
                logger.error("%s audit #%s failed — will retry next cycle", table_name, audit_id)

    def detect_and_push_local_changes(self, db):
        logger.info("=" * 60)
        logger.info("STARTING PUSH LOCAL CHANGES TO REMOTE")
        logger.info("=" * 60)

        cursor = None
        try:
            conn = db.connection
            cursor = conn.cursor(dictionary=True)

            # --- Calendar ---
            cursor.execute("""
                SELECT * FROM relation_calander_group_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            calendar_rows = cursor.fetchall()
            if not calendar_rows:
                logger.debug("No pending calendar changes to push")
            else:
                logger.info("Found %d pending calendar change(s)", len(calendar_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "relation_calander_group_audit",
                    calendar_rows,
                    {
                        "INSERT": lambda row: push_calendar_add(db, self.settings, row),
                        "UPDATE": lambda row: push_calendar_update(db, self.settings, row),
                        "DELETE": lambda row: push_calendar_delete(db, self.settings, row),
                    }
                )


            # --- Attendance ---
            cursor.execute("""
                SELECT * FROM attendance_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            attendance_rows = cursor.fetchall()
            if not attendance_rows:
                logger.debug("No pending attendance changes to push")
            else:
                logger.info("Found %d pending attendance change(s)", len(attendance_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "attendance_audit",
                    attendance_rows,
                    {
                        "ADD_STUDENT":       lambda row: push_add(db, self.settings, row),
                        "UPDATE":            lambda row: push_update(db, self.settings, row),
                        "INSERT_attendance": lambda row: send_new_attendance(db, self.settings, row),
                    }
                )


            # --- Account_Level ---
            cursor.execute("""
                SELECT * FROM account_level_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            account_level_rows = cursor.fetchall()
            if not account_level_rows:
                logger.debug("No pending AccountLevel changes to push")
            else:
                logger.info("Fount %d pending AccountLevel change(s)", len(account_level_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "account_level_audit",
                    account_level_rows,
                    {
                        "INSERT": lambda row: push_accountLevelAdd(db, self.settings, row),
                        "UPDATE": lambda row: push_accountLevelUpdate(db, self.settings, row),
                        "DELETE": lambda row: push_accountLevelDelete(db, self.settings, row),
                    }
                )


            # --- Account_Section ---
            cursor.execute("""
                SELECT * FROM account_section_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            account_section_rows = cursor.fetchall()
            if not account_section_rows:
                logger.debug("No pending AccountSection changes to push ")
            else:
                logger.info("Fount %d pending AccountSection change(s)", len(account_section_rows))
                self._process_audit_rows(
                    cursor,conn,
                    "account_section_audit",
                    account_section_rows,
                    {
                        "INSERT": lambda row: push_accountSectionAdd(db, self.settings, row),
                        "UPDATE": lambda  row: push_accountSectionUpdate(db, self.settings, row),
                        "DELETE": lambda row: push_accountSectionDelete(db, self.settings, row),
                    }
                )


            # --- Account_Subject
            cursor.execute("""
                SELECT * FROM account_subject_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            account_subject_rows = cursor.fetchall()
            if not account_subject_rows:
                logger.debug("No pending AccountSubject changes to push ")
            else:
                logger.info("Found %d pending AccountSubject change(s)", len(account_subject_rows))
                self._process_audit_rows(
                    cursor,conn,
                    "account_section_audit",
                    account_subject_rows,
                    {
                        "INSERT": lambda  row: push_accountSubjectAdd(db, self.settings, row),
                        "UPDATE": lambda  row: push_accountSubjectUpdate(db, self.settings, row),
                        "DELETE": lambda  row: push_accountSubjectDelete(db, self.settings, row),
                    }
                )

            # --- Account_Tag
            cursor.execute("""
                SELECT * FROM account_tag_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            account_tag_rows = cursor.fetchall()
            if not account_tag_rows:
                logger.debug("No pending AccountTag changes to push")
            else:
                logger.info("Found %s PENDING AccountTag change(s)", len(account_tag_rows))
                self._process_audit_rows(
                    cursor,conn,
                    "account_tag_audit",
                    account_tag_rows,
                    {
                        "INSERT": lambda row: push_accountTagAdd(db, self.settings, row),
                        "UPDATE": lambda row: push_accountTagUpdate(db, self.settings, row),
                        "DELETE": lambda  row: push_accountTagDelte(db, self.settings, row)
                    }
                )


        except Exception as e:
            logger.exception("Fatal error in data_pusher: %s", e)

        finally:
            if cursor:
                cursor.close()

        logger.info("=" * 60)
        logger.info("PUSH LOCAL CHANGES COMPLETED")
        logger.info("=" * 60)
