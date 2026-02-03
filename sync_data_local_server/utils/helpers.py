"""
Helper utilities for sync operations
Handles sync status file management
"""
import json
import os
from datetime import datetime


# File path for sync status
SYNC_STATUS_FILE = "data/sync_status.json"


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
            'updated_at': datetime.now().isoformat()
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

