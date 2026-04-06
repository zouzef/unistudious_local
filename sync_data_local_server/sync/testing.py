def push_calendar_add(self, row, db):
    """Handle calendar INSERT action"""
    try:
        import json

        new_data = json.loads(row.get('new_data', '{}'))
        group_id = new_data.get('group_id')
        local_calendar_id = row.get('id_calander')

        # ✅ Step 1: Check if group is special
        cursor_check = db.connection.cursor(dictionary=True)
        cursor_check.execute("SELECT is_special FROM relation_group_local_session WHERE id = %s", (group_id,))
        group = cursor_check.fetchone()
        cursor_check.close()

        is_special = group.get('is_special', False) if group else False

        # ✅ Step 2: Extract date/time from new_data
        start_datetime = new_data.get('start_time', '')
        end_datetime = new_data.get('end_time', '')
        start_time = start_datetime.split(' ')[1][:5] if start_datetime else None
        end_time = end_datetime.split(' ')[1][:5] if end_datetime else None

        # ✅ Step 3: Build base payload (shared between both APIs)
        payload = {
            'sessionId':   new_data.get('session_id'),
            'localId':     new_data.get('local_id'),
            'teacherId':   new_data.get('teacher_id'),
            'accountId':   new_data.get('account_id'),
            'startDate':   start_datetime.split(' ')[0] if start_datetime else None,
            'endDate':     '',
            'startTime':   start_time,
            'endTime':     end_time,
            'eventType':   'none',
            'typeSession': new_data.get('type'),
            'eventTitle':  new_data.get('title'),
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
                FROM relation_calander_group_session 
                WHERE id = %s
            """, (local_calendar_id,))
            extra = cursor_extra.fetchone()
            cursor_extra.close()

            if not extra:
                print(f"❌ Could not find calendar row #{local_calendar_id} for extra fields")
                return False

            # Add special-group-only fields to payload
            payload['capacity']   = extra.get('capacity')
            payload['accessType'] = extra.get('access_type')
            payload['groupId']    = group_id  # needed by special API

            print(f"📦 Special group payload: {payload}")
            success, remote_calendar_id, remote_group_id = _send_calendar_special_group(self.settings, payload)

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

                print(f"✅ Saved remote_calendar_id={remote_calendar_id} → relation_calander_group_session #{local_calendar_id}")
                print(f"✅ Saved remote_group_id={remote_group_id} → relation_group_local_session #{group_id}")

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

                print(f"✅ Saved remote_calendar_id={remote_calendar_id} → relation_calander_group_session #{local_calendar_id}")

        return success

    except Exception as e:
        print(f"❌ Error in push_calendar_add: {e}")
        import traceback
        traceback.print_exc()
        return False


def _send_calendar_special_group(settings, payload):
    """Send calendar event for SPECIAL groups — returns (success, remote_calendar_id, remote_group_id)"""
    try:
        response = requests.post(
            f"{settings['api_url']}/your-special-endpoint",  # ← replace with real endpoint
            json=payload,
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            data = response.json()
            remote_calendar_id = data.get('calendar_id')  # ← adjust to real key name
            remote_group_id    = data.get('group_id')     # ← adjust to real key name
            return True, remote_calendar_id, remote_group_id
        else:
            print(f"❌ Special API error: {response.status_code} - {response.text}")
            return False, None, None
    except Exception as e:
        print(f"❌ Exception in _send_calendar_special_group: {e}")
        return False, None, None