import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync.pushers.attendance_pusher import push_add, push_update

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

    def detect_and_push_local_changes(self, db):
        print("\n" + "="*60)
        print("🚀 STARTING PUSH LOCAL CHANGES TO REMOTE")
        print("="*60)

        cursor = None
        try:
            conn = db.connection
            cursor = conn.cursor(dictionary=True)

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
						"UPDATE": lambda row: push_update(db, self.settings, row)
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