from core.database import Database

def find_by_id(table, id_value=None, id_column='id', extra_where=None, extra_params=None, enabled_only=True):
    """
    Generic 'findById' — returns the row (dict) if found, else None.

    Args:
        table: table name, e.g. 'user', 'session', 'virtual_user'
        id_value: the id to look up (pass None to skip the id filter entirely)
        id_column: primary key column name (default 'id')
        extra_where: extra SQL condition string, e.g. "account_id = %s"
        extra_params: tuple of params matching extra_where placeholders
        enabled_only: if True, adds "AND enabled = 1"
    """
    where_clauses = []
    params = []

    if id_value is not None:
        where_clauses.append(f"{id_column} = %s")
        params.append(id_value)

    if extra_where:
        where_clauses.append(extra_where)
        if extra_params:
            params.extend(extra_params)

    if enabled_only:
        where_clauses.append("enabled = 1")

    if not where_clauses:
        raise ValueError("find_by_id requires at least id_value or extra_where to be set")

    query = f"SELECT * FROM {table} WHERE {' AND '.join(where_clauses)}"

    result = Database.execute_query(query, tuple(params), fetch=True)

    return result[0] if result else None


def exists_by_id(table, id_value=None, id_column='id', extra_where=None, extra_params=None, enabled_only=True):
    """Lightweight boolean check — same filters as find_by_id but no full row fetch."""
    return find_by_id(table, id_value, id_column, extra_where, extra_params, enabled_only) is not None