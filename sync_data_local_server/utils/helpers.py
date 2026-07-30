"""
Helper utilities for sync operations
Handles sync status file management
"""
import json
import os
from datetime import datetime,timedelta


# File path for sync status
SYNC_STATUS_FILE = "data/sync_status.json"

print(SYNC_STATUS_FILE)

def format_date(date_value):
    """
    Format date value for MySQL storage
    Handles various input formats and converts to MySQL datetime format

    Args:
        date_value: Date string, datetime object, or None

    Returns:
        str: MySQL-compatible datetime string (YYYY-MM-DD HH:MM:SS) or None
    """
    if date_value is None:
        return None

    try:
        # If already a datetime object
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d %H:%M:%S')

        # If it's a string, try to parse it
        if isinstance(date_value, str):
            # Try ISO format first (most common from APIs)
            try:
                dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

            # Try other common formats
            common_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
            ]

            for fmt in common_formats:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue

            # If nothing worked, return None
            print(f"⚠️  Could not parse date format: {date_value}")
            return None

        # If it's a timestamp (int or float)
        if isinstance(date_value, (int, float)):
            dt = datetime.fromtimestamp(date_value)
            return dt.strftime('%Y-%m-%d %H:%M:%S')

        print(f"⚠️  Unsupported date type: {type(date_value)}")
        return None

    except Exception as e:
        print(f"❌ Error formatting date {date_value}: {e}")
        return None

def get_last_sync_time():
    """
    Get the last sync time from status file

    Returns:
        datetime: Last sync time or None if not available
    """
    try:
        # Check if file exists
        if not os.path.exists(SYNC_STATUS_FILE):
            print("ℹ️  Sync status file does not exist (first sync)")
            return None

        # Read the file
        with open(SYNC_STATUS_FILE, 'r') as f:
            data = json.load(f)

        # Get last_sync_time field
        last_sync_str = data.get('last_sync_time')

        if not last_sync_str:
            print("⚠️  No valid sync time found in file")
            return None

        # Convert ISO string to datetime
        last_sync_time = datetime.fromisoformat(last_sync_str)
        print(f"📅 Last sync time from file: {last_sync_time}")

        return last_sync_time

    except json.JSONDecodeError as e:
        print(f"❌ Error reading sync status file (invalid JSON): {e}")
        print("ℹ️  Will perform full sync")
        return None

    except ValueError as e:
        print(f"❌ Error parsing sync time (invalid format): {e}")
        print("ℹ️  Will perform full sync")
        return None

    except FileNotFoundError:
        print("ℹ️  Sync status file not found (first sync)")
        return None

    except Exception as e:
        print(f"❌ Unexpected error reading sync status: {e}")
        print("ℹ️  Will perform full sync")
        return None

def safe_int(value):
    """
    Safely convert a value to int for DB insertion.
    Returns None if the value is not a valid integer (e.g. "unknown", "", None).
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        # handles "123", "123.0", etc. Strings like "unknown" will fail here.
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None

def save_last_sync_time(sync_time):
    """
    Save the last sync time to status file

    Args:
        sync_time: datetime object to save
    """
    try:
        # Validate input
        if not isinstance(sync_time, datetime):
            raise ValueError("sync_time must be a datetime object")

        # Create data directory if it doesn't exist
        data_dir = os.path.dirname(SYNC_STATUS_FILE)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"📁 Created directory: {data_dir}")

        # Create backup of existing file (optional but recommended)
        if os.path.exists(SYNC_STATUS_FILE):
            backup_file = f"{SYNC_STATUS_FILE}.backup"
            try:
                with open(SYNC_STATUS_FILE, 'r') as original:
                    with open(backup_file, 'w') as backup:
                        backup.write(original.read())
                print(f"💾 Backup created: {backup_file}")
            except Exception as e:
                print(f"⚠️  Could not create backup: {e}")

        # Prepare sync data
        sync_data = {
            'last_sync_time': sync_time.isoformat(),
            'updated_at': (datetime.now() - timedelta(hours=1)).isoformat()
        }

        # Write to file
        with open(SYNC_STATUS_FILE, 'w') as f:
            json.dump(sync_data, f, indent=2)

        print(f"✅ Sync time saved to file: {sync_time}")

    except ValueError as e:
        print(f"❌ Invalid input: {e}")

    except OSError as e:
        print(f"❌ Error creating directory or file: {e}")

    except Exception as e:
        print(f"❌ Error saving sync time to file: {e}")

def check_internet_connection(url="https://www.google.com", timeout=5):
    """
    Check if internet connection is available

    Args:
        url: URL to check (default: google.com)
        timeout: Request timeout in seconds

    Returns:
        bool: True if internet is available, False otherwise
    """
    try:
        import requests
        print("🌐 Checking internet connection...")
        response = requests.get(url, timeout=timeout)

        if response.status_code == 200:
            print("✅ Internet connection available")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False

    except requests.ConnectionError:
        print("❌ No internet connection available")
        return False

    except requests.Timeout:
        print("❌ Connection timeout")
        return False

    except Exception as e:
        print(f"❌ Error checking internet connection: {e}")
        return False

def get_mac_address(db):
    """
    Get the mac address of this slc from the database
    :param db:
    :return:
    """
    try:
        query = "SELECT username FROM slc LIMIT 1"
        result = db.fetch_query(query)
        if result and result[0].get('username'):
            mac = result[0]['username']
            print(f"✅ MAC address found: {mac}")
            return mac
        print("❌ No MAC address found in slc table")
        return None
    except Exception as e:
        print(f"❌ Error getting MAC address from database: {e}")
        return None

def reset_attendance_token(settings, attendance_id):
    """
    Reset the token for an attendance record on the remote server
    """
    try:
        from core.auth import get_token
        import requests

        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        print("attendance_id from reset attendance_token: \n \n \n \n \n",attendance_id,"\n \n \n \n \n")
        payload = {
            "entityId": str(attendance_id),
            "entityName": "Attendance"
        }

        url = f"{settings.api_base_url}/slc/reset-special-slc-token-detail-by-id"  # ← confirm this URL
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        print("reset_attendance_function:",response)
        if response.status_code == 200:
            print(f"      🔄 Token reset successfully for attendance {attendance_id}")
            return True
        else:
            print(f"      ⚠️  Token reset failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"      ❌ Error resetting token: {e}")
        return False

def get_all_calendar_ids(db):
    """
    Load all calendar id mappings into a dict
    {id_prod: local_id }
    :param db:
    :return:
    """
    try:
        result = db.fetch_query(
            "SELECT id, id_prod FROM relation_calander_group_session WHERE id_prod IS NOT NULL "
        )
        mapping = {row['id_prod']: row['id'] for row in result}
        print(f"      🔗 Loaded {len(mapping)} calendar mappings")
        return mapping
    except Exception as e:
        print(f"      ❌ Error loading calendar mappings: {e}")
        return {}

def get_all_group_ids(db):
    """
    Load all group id mappings into a dict
    { id_prod: local_id }
    """
    try:
        result = db.fetch_query(
            "SELECT id, id_prod FROM relation_group_local_session WHERE id_prod IS NOT NULL"
        )
        mapping = {row['id_prod']: row['id'] for row in result}
        print(f"      🔗 Loaded {len(mapping)} group mappings")
        return mapping
    except Exception as e:
        print(f"      ❌ Error loading group mappings: {e}")
        return {}

def _find_key_by_prefix(data, prefix):
    """
    new_data stores keys like 'deleteRelationIds[0,1]' with a dynamic
    index suffix baked into the key name. This finds the actual key
    regardless of what's inside the brackets and returns its value.
	"""
    for key, value in data.items():
        if key.startswith(prefix):
            return value
    return []

def _map_ids_to_prod(db, table, id_field, local_ids):
    """Given a list of local ids, return {local_id: id_prod} for that table."""
    if not local_ids:
        return {}
    cursor = db.connection.cursor(dictionary=True)
    placeholders = ",".join(["%s"] * len(local_ids))
    cursor.execute(
        f"SELECT id, id_prod FROM {table} WHERE {id_field} IN ({placeholders})",
        tuple(local_ids)
    )
    rows = cursor.fetchall()
    cursor.close()
    return {row['id']: row['id_prod'] for row in rows}

def _map_subject_ids_to_prod(db, local_ids):
    """
    subjectId values coming from the frontend/audit are account_subject.id.
    Resolve directly to account_subject.id_prod.
    """
    if not local_ids:
        return {}

    cursor = db.connection.cursor(dictionary=True)
    placeholders = ",".join(["%s"] * len(local_ids))
    cursor.execute(
       f"SELECT id, id_prod FROM account_subject WHERE id IN ({placeholders})",
       tuple(local_ids)
    )
    rows = cursor.fetchall()
    cursor.close()

    return {row['id']: row['id_prod'] for row in rows}

def _flatten_group_payload_to_form(payload):
    """
    Convert the group-update payload into PHP-style bracket form-data fields.
    e.g. updateRelations: [{"id":237,"teacherId":4,"subjectId":1}]
    ->  updateRelations[0][id]=237, updateRelations[0][teacherId]=4, updateRelations[0][subjectId]=1
    """
    form_data = []

    form_data.append(("name", payload.get("name")))
    form_data.append(("capacity", payload.get("capacity")))

    for i, val in enumerate(payload.get("deleteRelationIds", [])):
        form_data.append((f"deleteRelationIds[{i}]", val))

    for i, rel in enumerate(payload.get("updateRelations", [])):
        form_data.append((f"updateRelations[{i}][id]", rel.get("id")))
        form_data.append((f"updateRelations[{i}][teacherId]", rel.get("teacherId")))
        form_data.append((f"updateRelations[{i}][subjectId]", rel.get("subjectId")))

    for i, val in enumerate(payload.get("newRelationTeacherId", [])):
        form_data.append((f"newRelationTeacherId[{i}]", val))

    for i, val in enumerate(payload.get("newRelationSubjectId", [])):
        form_data.append((f"newRelationSubjectId[{i}]", val))

    return form_data