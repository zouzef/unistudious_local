import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync.pushers.attendance_pusher import push_add, push_update,send_new_attendance
from sync.pushers.calendar_pusher import _send_calendar, _send_update_calander, _send_delete_calander,_send_calendar_special_group

class DataPusher:

    def __init__(self, settings):
        self.settings = settings

    def _process_audit_rows(self, cursor, conn, table_name, rows, action_handlers):
        for row in rows:
            audit_id = row['audit_id']
            action = row['action_type']

            print(f"\n🔄 Processing {table_name} audit #{audit_id} | action = {action}")

            handler = action_handlers.get(action)

            if not handler:
                print(f"⚠️  Unknown action: {action} — skipping")
                continue

            success = handler(row)

            if success:
                cursor.execute(f"""
                    UPDATE {table_name} 
                    SET is_synced = 1 
                    WHERE audit_id = %s
                """, (audit_id,))
                conn.commit()
                print(f"✅ {table_name} audit #{audit_id} marked as synced")
            else:
                print(f"❌ {table_name} audit #{audit_id} failed — will retry next cycle")

    def push_calendar_add(self, row, db):
        """Handle calendar INSERT action"""
        try:
            import json

            new_data = json.loads(row.get('new_data', '{}'))
            group_id = new_data.get('group_id')
            local_calendar_id = row.get('id_calander')

            # ✅ Step 1: Check if group is special
            cursor_check = db.connection.cursor(dictionary=True)
            cursor_check.execute("SELECT special_group FROM relation_group_local_session WHERE id = %s", (group_id,))
            group = cursor_check.fetchone()
            cursor_check.close()

            is_special = group.get('special_group', False) if group else False
            print('is_special resullt: ',is_special)
            # ✅ Step 2: Extract date/time from new_data
            start_datetime = new_data.get('start_time', '')
            end_datetime = new_data.get('end_time', '')
            start_time = start_datetime.split(' ')[1][:5] if start_datetime else None
            end_time = end_datetime.split(' ')[1][:5] if end_datetime else None

            # ✅ Step 3: Build base payload (shared between both APIs)
            payload = {
                'sessionId': new_data.get('session_id'),
                'localId': new_data.get('local_id'),
                'teacherId': new_data.get('teacher_id'),
                'accountId': new_data.get('account_id'),
                'startDate': start_datetime.split(' ')[0] if start_datetime else None,
                'endDate': '',
                'startTime': start_time,
                'endTime': end_time,
                'eventType': 'none',
                'typeSession': new_data.get('type'),
                'eventTitle': new_data.get('title'),
                'description': new_data.get('description'),
                'completionTag': [],
            }

            if new_data.get('room_id'):
                payload['roomId'] = new_data.get('room_id')
            if new_data.get('subject_id'):
                payload['subjectId'] = new_data.get('subject_id')

            # ✅ Step 4: Route based on group type
            if is_special:
                print(f"⭐ Group {group_id} is SPECIAL — fetching extra fields from DB")

                # Fetch capacity and accessType from the main calendar table
                cursor_extra = db.connection.cursor(dictionary=True)
                cursor_extra.execute("""
                    SELECT capacity, access_type 
                    FROM relation_group_local_session 
                    WHERE id = %s
                """, (group_id,))
                extra = cursor_extra.fetchone()
                cursor_extra.close()

                if not extra:
                    print(f"❌ Could not find calendar row #{local_calendar_id} for extra fields")
                    return False

                # Add special-group-only fields to payload
                payload['endDate'] = payload['startDate']
                payload['capacity'] = extra.get('capacity')
                payload['accessType'] = extra.get('access_type')
                payload['groupId'] = group_id  # needed by special API



                result = _send_calendar_special_group(self.settings, payload)
                print("\n \n \n \n",result)
                if result is None:
                    print("❌ _send_calendar_special_group returned None — check the pusher function")
                    return False
                success, remote_calendar_id, remote_group_id = result

                if success and remote_calendar_id and remote_group_id:
                    cursor_save = db.connection.cursor()

                    # Save remote_calendar_id → relation_calander_group_session.id_prod
                    cursor_save.execute("""
                        UPDATE relation_calander_group_session 
                        SET id_prod = %s 
                        WHERE id = %s
                    """, (remote_calendar_id, local_calendar_id))

                    # Save remote_group_id → relation_group_local_session.id_prod
                    cursor_save.execute("""
                        UPDATE relation_group_local_session 
                        SET id_prod = %s 
                        WHERE id = %s
                    """, (remote_group_id, group_id))

                    db.connection.commit()
                    cursor_save.close()

                    print(
                        f"✅ Saved remote_calendar_id={remote_calendar_id} → relation_calander_group_session #{local_calendar_id}")
                    print(f"✅ Saved remote_group_id={remote_group_id} → relation_group_local_session #{group_id}")

                elif not(success):
                    print("Change the is_synced to 2")
                    cursor_save = db.connection.cursor()

                    # Save remote_calendar_id → relation_calander_group_session.id_prod
                    cursor_save.execute("""
                        UPDATE relation_calander_group_audit 
                        SET is_synced = 2
                        WHERE id_calander = %s
                    """,(local_calendar_id,))

                    db.connection.commit()
                    cursor_save.close()

            else:
                print(f"👥 Group {group_id} is NORMAL — using standard API")
                payload['groupId'] = new_data.get('group_id')

                print(f"📦 Normal group payload: {payload}")
                success, remote_calendar_id = _send_calendar(self.settings, payload)

                if success and remote_calendar_id:
                    cursor_save = db.connection.cursor()
                    cursor_save.execute("""
                        UPDATE relation_calander_group_session 
                        SET id_prod = %s 
                        WHERE id = %s
                    """, (remote_calendar_id, local_calendar_id))
                    db.connection.commit()
                    cursor_save.close()

                    print(
                        f"✅ Saved remote_calendar_id={remote_calendar_id} → relation_calander_group_session #{local_calendar_id}")

            return success

        except Exception as e:
            print(f"❌ Error in push_calendar_add: {e}")
            import traceback
            traceback.print_exc()
            return False

    def push_calendar_update(self, row, db):
        """Handle calendar UPDATE action"""
        try:
            calendar_id = row.get('calendar_id')
            payload = {
                'calendar_date': row.get('calendar_date'),
                'start_time': row.get('start_time'),
                'end_time': row.get('end_time'),
            }
            success = _send_update_calander(self.settings, calendar_id, payload)
            return success
        except Exception as e:
            print(f"❌ Error in push_calendar_update: {e}")
            return False

    def push_calendar_delete(self, row, db):
        """Handle calendar DELETE action"""
        try:
            calendar_id = row.get('calendar_id')
            payload = {}
            success = _send_delete_calander(self.settings, calendar_id, payload)
            return success
        except Exception as e:
            print(f"❌ Error in push_calendar_delete: {e}")
            return False

    def detect_and_push_local_changes(self, db):
        print("\n" + "="*60)
        print("🚀 STARTING PUSH LOCAL CHANGES TO REMOTE")
        print("="*60)

        cursor = None
        try:
            conn = db.connection
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                            SELECT * FROM relation_calander_group_audit
                            WHERE is_synced = 0
                            ORDER BY audit_id ASC
                        """)
            calendar_rows = cursor.fetchall()
            print("\n \n \n \n \n \n \n ", calendar_rows)
            if not calendar_rows:
                print(" No pending calendar changes to push")
            else:
                print(f"📋 Found {len(calendar_rows)} pending calendar change(s)")
                self._process_audit_rows(
                    cursor, conn,
                    "relation_calander_group_audit",
                    calendar_rows,
                    {
                        "INSERT": lambda row: self.push_calendar_add(row, db),  # ✅ CORRECT
                        "UPDATE": lambda row: self.push_calendar_update(row, db),  # ✅ CORRECT
                        "DELETE": lambda row: self.push_calendar_delete(row, db)  # ✅ CORRECT
                    }
                )



            cursor.execute("""
                SELECT * FROM attendance_audit 
                WHERE is_synced = 0 
                ORDER BY audit_id ASC
            """)
            attendance_rows = cursor.fetchall()

            if not attendance_rows:
                print("ℹ️  No pending attendance changes to push")
            else:
                print(f"📋 Found {len(attendance_rows)} pending attendance change(s)")
                self._process_audit_rows(
                    cursor, conn,
                    "attendance_audit",
                    attendance_rows,
					{
						"ADD_STUDENT": lambda row: push_add(db, self.settings, row),
						"UPDATE": lambda row: push_update(db, self.settings, row),
                        "INSERT_attendance": lambda  row: send_new_attendance(db,self.settings,row),
					}
                )


        except Exception as e:
            print(f"❌ Fatal error in data_pusher: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if cursor:
                cursor.close()

        print("\n" + "="*60)
        print("✅ PUSH LOCAL CHANGES COMPLETED")
        print("="*60)

if __name__ == "__main__":
    import time
    from datetime import datetime
    from config.settings import get_settings
    from core.database import Database
    from core.auth import init_auth,start_auto_refresh

    # Load settings properly
    settings = get_settings("config/config.json")

    # Init auth (needed for API calls in pushers)
    init_auth(settings)
    start_auto_refresh()
    time.sleep(1)

    while True:
        print(f"\n Running at {datetime.now()}")

        db = Database(settings)
        db.connect()

        pusher = DataPusher(settings)
        pusher.detect_and_push_local_changes(db)

        db.disconnect()

        print(f"\n Waiting 60 seconds before next check ...")
        time.sleep(60)