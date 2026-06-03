"""
Audit Helper
Shared utility for logging audit records across all modules
"""
import json
import sys
import os
from datetime import datetime, date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database


def serialize_for_audit(obj):
    """Custom JSON serializer for types not serializable by default."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def log_audit(table_name, action_type, old_data=None, new_data=None, record_id=None):
    """
    Insert a record into any audit table.

    Args:
        table_name:  The audit table to write to (e.g. 'account_level_audit', 'account_section_audit')
        action_type: 'INSERT', 'UPDATE', or 'DELETE'
        old_data:    dict of the record BEFORE the change (None for INSERT)
        new_data:    dict of the record AFTER the change  (None for DELETE)
        record_id:   ID of the affected record (only for tables that have a record_id column)
    """
    try:
        if record_id is not None:
            audit_query = f"""
                INSERT INTO {table_name} (action_type, record_id, old_data, new_data)
                VALUES (%s, %s, %s, %s)
            """
            params = (
                action_type,
                record_id,
                json.dumps(old_data, default=serialize_for_audit) if old_data else None,
                json.dumps(new_data, default=serialize_for_audit) if new_data else None
            )
        else:
            audit_query = f"""
                INSERT INTO {table_name} (action_type, old_data, new_data)
                VALUES (%s, %s, %s)
            """
            params = (
                action_type,
                json.dumps(old_data, default=serialize_for_audit) if old_data else None,
                json.dumps(new_data, default=serialize_for_audit) if new_data else None
            )

        Database.execute_query(audit_query, params, fetch=False)

    except Exception as e:
        print(f"⚠️  Audit log failed [{table_name}]: {e}")