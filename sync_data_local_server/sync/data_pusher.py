import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sync.pushers import (
    attendance_pusher,
    calendar_pusher,
    accountLevel_pusher,
    accountSection_pusher,
    accountSubject_pusher,
    accountTag_pusher,
    completionTag_pusher,
    association_pusher,
    slcdoor_pusher,
    camera_pusher,
    tablet_pusher,
    user_pusher,
    virtuel_pusher,
    group_pusher
)

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

            # ============================================ PRESENCE ============================================

            # --- Calendar ---
            cursor.execute("""
                SELECT * 
                 FROM relation_calander_group_audit
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
                        "INSERT": lambda row: calendar_pusher.push_calendar_add(db, self.settings, row),
                        "UPDATE": lambda row: calendar_pusher.push_calendar_update(db, self.settings, row),
                        "DELETE": lambda row: calendar_pusher.push_calendar_delete(db, self.settings, row),
                    }
                )

            # --- Attendance ---
            cursor.execute("""
                SELECT * 
                 FROM attendance_audit
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
                        "ADD_STUDENT":       lambda row: attendance_pusher.push_add(db, self.settings, row),
                        "UPDATE":            lambda row: attendance_pusher.push_update(db, self.settings, row),
                        "INSERT_attendance": lambda row: attendance_pusher.send_new_attendance(db, self.settings, row),
                    }
                )

            # ============================================ CONFIGURATION ============================================

            # --- Account_Level ---
            cursor.execute("""
                SELECT * 
                 FROM account_level_audit
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
                        "INSERT": lambda row: accountLevel_pusher.push_accountLevelAdd(db, self.settings, row),
                        "UPDATE": lambda row: accountLevel_pusher.push_accountLevelUpdate(db, self.settings, row),
                        "DELETE": lambda row: accountLevel_pusher.push_accountLevelDelete(db, self.settings, row),
                    }
                )

            # --- Account_Section ---
            cursor.execute("""
                SELECT * 
                 FROM account_section_audit
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
                        "INSERT": lambda  row: accountSection_pusher.push_accountSectionAdd(db, self.settings, row),
                        "UPDATE": lambda  row: accountSection_pusher.push_accountSectionUpdate(db, self.settings, row),
                        "DELETE": lambda  row: accountSection_pusher.push_accountSectionDelete(db, self.settings, row),
                    }
                )

            # --- Account_Subject
            cursor.execute("""
                SELECT * 
                 FROM account_subject_audit
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
                    "account_subject_audit",
                    account_subject_rows,
                    {
                        "INSERT": lambda  row: accountSubject_pusher.push_accountSubjectAdd(db, self.settings, row),
                        "UPDATE": lambda  row: accountSubject_pusher.push_accountSubjectUpdate(db, self.settings, row),
                        "DELETE": lambda  row: accountSubject_pusher.push_accountSubjectDelete(db, self.settings, row),
                    }
                )

            # --- Account_Tag
            cursor.execute("""
                SELECT * 
                 FROM account_tag_audit
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
                        "INSERT": lambda row: accountTag_pusher.push_accountTagAdd(db, self.settings, row),
                        "UPDATE": lambda row: accountTag_pusher.push_accountTagUpdate(db, self.settings, row),
                        "DELETE": lambda row: accountTag_pusher.push_accountTagDelete(db, self.settings, row)
                    }
                )

            # --- Compltetion_Tag ---
            cursor.execute("""
                SELECT * 
                 FROM completion_tag_account_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            completion_tag_rows = cursor.fetchall()
            if not completion_tag_rows:
                logger.debug("No pending CompletionTag changes to push")
            else:
                logger.info("Found %s PENDING CompletionTag change(s)", len(completion_tag_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "completion_tag_account_audit",
                    completion_tag_rows,
                    {
                        "INSERT": lambda row: completionTag_pusher.push_completionTagAdd(db, self.settings, row),
                        "UPDATE": lambda row: completionTag_pusher.push_completionTagUpdate(db, self.settings, row),
                        "DELETE": lambda row: completionTag_pusher.push_completionTagDelete(db, self.settings, row)
                    }
                )

            # --- Association Folder ---
            cursor.execute("""
                SELECT * 
                 FROM sync_folders
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            folder_not_associated = cursor.fetchall()
            if not folder_not_associated:
                logger.debug("No pending Association Folder changes to push")
            else:
                logger.debug("Found %s Assocication Folder change(s)", len(folder_not_associated))
                self._process_audit_rows(
                    cursor,conn,
                    "sync_folders",
                    folder_not_associated,
                    {
                        "INSERT": lambda row: association_pusher.push_FolderNotAssociated(db, self.settings, row),
                        # "UPDATE": lambda row: push_AssociationUpdate(db, self.settings, row),
                        # "DELETE": lambda row: push_AssociationDelete(db, self.settings, row)
                    }
                )


            # --- Association_Sync ---
            cursor.execute("""
                SELECT * 
                 FROM sync_images
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            assocation_rows = cursor.fetchall()
            if not assocation_rows:
                logger.debug("No pending Association changes to push")
            else:
                logger.debug("Found %s PENDING Associaion change(s)", len(assocation_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "sync_images",
                    assocation_rows,
                    {
                        "INSERT": lambda row: association_pusher.push_AssociationAdd(db, self.settings, row),
                        "UPDATE": lambda row: association_pusher.push_AssociationUpdate(db, self.settings, row),
                        "DELETE": lambda row: association_pusher.push_AssociationDelete(db, self.settings, row)
                    }
                )

            # ============================================ SLC DEVICES ============================================
            # --- slc_door ---
            cursor.execute("""
                SELECT * 
                 FROM slc_door_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
                """)
            slcdoor_rows = cursor.fetchall()
            if not slcdoor_rows:
                logger.debug("No pending SlcDoor changes to push")
            else:
                logger.debug("Found %s PENDING door change(s)", len(slcdoor_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "slc_door_audit",
                    slcdoor_rows,
                    {
                        'INSERT': lambda row: slcdoor_pusher.push_doorAdd(db, self.settings, row),
                        'UPDATE': lambda row: slcdoor_pusher.push_doorUpdate(db, self.settings, row),
                        'DELETE': lambda row: slcdoor_pusher.push_doorDelete(db, self.settings, row)
                    }
                )

            # --- camera ---
            cursor.execute("""
                SELECT * 
                 FROM camera_audit
                 WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            camera_rows = cursor.fetchall()
            if not camera_rows:
                logger.debug("No pending camera changes to push")
            else:
                logger.debug("Found %s PENDING camera change(s)", len(camera_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "camera_audit",
                    camera_rows,
                    {
                        'INSERT': lambda row: camera_pusher.push_cameraAdd(db, self.settings, row),
                        'UPDATE': lambda row: camera_pusher.push_cameraUpdate(db, self.settings, row),
                        'DELETE': lambda row: camera_pusher.push_cameraDelete(db, self.settings, row)
                    }
                )

            # --- tablet ---
            cursor.execute("""
                SELECT * 
                 FROM tablet_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            tablet_rows = cursor.fetchall()
            if not tablet_rows:
                logger.debug("No pending tablet changes to push")
            else:
                logger.debug("Found %s PENDING tablet change(s)", len(tablet_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "tablet_audit",
                    tablet_rows,
                    {
                        'INSERT': lambda row: tablet_pusher.push_tabletAdd(db, self.settings, row),
                        'UPDATE': lambda row: tablet_pusher.push_tabletUpdate(db, self.settings, row),
                        'DELETE': lambda row: tablet_pusher.push_tabletDelete(db, self.settings, row)
                    }
                )

            # ============================================ USER ============================================
            # --- User ---
            cursor.execute("""
                SELECT * 
                 FROM user_audit
                WHERE is_synced = 0
                ORDER BY audit_id ASC
            """)
            user_rows = cursor.fetchall()
            if not user_rows:
                logger.debug("No pending User changes to push")
            else:
                logger.info("Found %d pending User change(s)", len(user_rows))
                self._process_audit_rows(
                    cursor, conn,
                    "user_audit",
                    user_rows,
                    {
                        "CREATE":      lambda row: user_pusher.push_userAdd(db, self.settings, row),
                        "UPDATE":      lambda row: user_pusher.push_userUpdate(db, self.settings, row),
                        "DELETE":      lambda row: user_pusher.push_userDelete(db, self.settings, row),
                        "ASSOCIATION": lambda row: user_pusher.push_userAssociation(db, self.settings, row)

                    }
                )

            # --- virtual_user ---
            cursor.execute("""
                SELECT * 
                 FROM virtual_user_audit
                WHERE is_synced = 0
                ORDER BY audit_id
            """)
            virtuel_user_rows = cursor.fetchall()
            if not virtuel_user_rows:
                logger.debug("No pending VirtuelUser changes to push")
            else:
                logger.info("Found %d pending virtuel_user_rows change(s)", len(virtuel_user_rows))
                self._process_audit_rows(
                    cursor,conn,
                    "virtual_user_audit",
                    virtuel_user_rows,
                    {
                        "CREATE":     lambda row: virtuel_pusher.push_virtuelAdd(db, self.settings, row),
                        "UPDATE":     lambda row: virtuel_pusher.push_virtuelUpdate(db, self.settings, row),
                        "DELETE":     lambda row: virtuel_pusher.push_virtuelDelete(db, self.settings, row),
                        "ASSOCIATE":  lambda row: virtuel_pusher.push_virtuelAssociate(db, self.settings, row),
                        "DISSOCIATE": lambda row: virtuel_pusher.push_virtuelDissociate(db, self.settings, row)
                    }
                )

            # --- Group ---
            cursor.execute("""
                SELECT * 
                 FROM relation_group_local_session_audit
                WHERE is_synced = 0
                ORDER BY audit_id
             """)
            group_rows = cursor.fetchall()
            if not group_rows:
                logger.debug("No pending Group changes to push")
            else:
                logger.info("Found %d pending Group chane(s)", len(group_rows))
                self._process_audit_rows(
                    cursor,
                    conn,
                    "relation_group_local_session_audit",
                    group_rows,
                    {
                        "INSERT":    lambda row:    group_pusher.push_groupAdd(db, self.settings,row),
                        "UPDATE":    lambda row:    group_pusher.push_groupUpdate(db, self.settings,row),
                        "DELETE":    lambda row:    group_pusher.push_groupDelete(db, self.settings, row),
                        "AFFECT":    lambda row:    group_pusher.push_affect_user(db, self.settings, row),
                        "DISAFFECT": lambda row:    group_pusher.push_disaffect_user(db, self.settings, row)
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
