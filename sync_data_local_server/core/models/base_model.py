"""
Base Model - Foundation for all table models
"""


class Column:
    def __init__(self, name, col_type, primary_key=False, auto_increment=False,
                 nullable=True, default=None, unique=False, on_update=None, comment=None):
        self.name = name
        self.col_type = col_type
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.on_update = on_update
        self.comment = comment

    def to_sql(self):
        parts = [f"`{self.name}`", self.col_type]

        is_timestamp = self.col_type.upper() == "TIMESTAMP"

        if is_timestamp:
            # TIMESTAMP columns: always explicitly NULL, then DEFAULT NULL
            # This avoids "Invalid default value" in strict MySQL mode
            parts.append("NULL")
            if self.default is not None:
                parts.append(f"DEFAULT {self.default}")
            else:
                parts.append("DEFAULT NULL")
        else:
            if not self.nullable:
                parts.append("NOT NULL")

            if self.default is not None:
                parts.append(f"DEFAULT {self.default}")
            elif self.nullable:
                parts.append("DEFAULT NULL")

        if self.on_update:
            parts.append(f"ON UPDATE {self.on_update}")

        if self.auto_increment:
            parts.append("AUTO_INCREMENT")

        return " ".join(parts)


class BaseModel:
    table_name = None
    columns = []
    charset = "utf8mb4"
    collate = "utf8mb4_unicode_ci"
    engine = "InnoDB"

    @classmethod
    def get_create_table_sql(cls):
        col_defs = []
        pk_col = None

        for col in cls.columns:
            col_defs.append(f"  {col.to_sql()}")
            if col.primary_key:
                pk_col = col.name

        if pk_col:
            col_defs.append(f"  PRIMARY KEY (`{pk_col}`)")

        cols_sql = ",\n".join(col_defs)

        return (
            f"CREATE TABLE IF NOT EXISTS `{cls.table_name}` (\n"
            f"{cols_sql}\n"
            f") ENGINE={cls.engine} DEFAULT CHARSET={cls.charset} "
            f"COLLATE={cls.collate};"
        )

    @classmethod
    def get_column_names(cls):

        return [col.name for col in cls.columns]

