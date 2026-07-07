from core.database import Database
from core.middleware import token_required
from core.checks import *



def reasign_user_data(table_name, old_user_id, new_user_id, extra_condition=None)

	query = f"UPDATE {table_name} SET use_id = %s WHERE user_id = %s"
	values = (new_user_id, old_user_id)

	if extra_condition:
		query += f" AND {extra_condition}"

	Database.execute_query(query, values, fetch=False)
