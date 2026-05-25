"""
Database Initializer
Runs once at startup — creates the database if missing, then creates or
migrates every table defined in core/models/models.py.
"""

import mysql.connector
from mysql.connector import Error

from core.models.models import ALL_MODELS


class DatabaseInitializer:

    def __init__(self, settings):
        self.settings = settings
        self.db_config = settings.database_config
        self.db_name = self.db_config["database"]

    def initialize(self):
        print("\n" + "=" * 60)
        print("🗄️  DATABASE INITIALIZER")
        print("=" * 60)

        conn = self._connect_without_db()
        if not conn:
            return False

        try:
            cursor = conn.cursor(dictionary=True)
            self._create_database(cursor)
            cursor.execute(f"USE `{self.db_name}`")

            total = len(ALL_MODELS)
            created = 0
            migrated = 0

            for model in ALL_MODELS:
                result = self._sync_table(cursor, conn, model)
                if result == "created":
                    created += 1
                elif result == "migrated":
                    migrated += 1

            conn.commit()
            print(f"\n✅ Initialization complete — "
                  f"{created} table(s) created, {migrated} migrated, "
                  f"{total - created - migrated} already up to date.")
            print("=" * 60 + "\n")
            return True

        except Error as e:
            print(f"❌ Initialization error: {e}")
            return False

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def _connect_without_db(self):
        try:
            conn = mysql.connector.connect(
                host=self.db_config["host"],
                port=self.db_config.get("port", 3306),
                user=self.db_config["user"],
                password=self.db_config["password"],
            )
            print(f"✅ Connected to MySQL server at {self.db_config['host']}")
            return conn
        except Error as e:
            print(f"❌ Cannot connect to MySQL: {e}")
            return None

    def _create_database(self, cursor):
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{self.db_name}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"✅ Database `{self.db_name}` ready")

    def _sync_table(self, cursor, conn, model):
        table = model.table_name

        cursor.execute(
            "SELECT COUNT(*) as cnt FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s",
            (self.db_name, table),
        )
        exists = cursor.fetchone()["cnt"] > 0

        if not exists:
            sql = model.get_create_table_sql()
            cursor.execute(sql)
            conn.commit()
            print(f"   ✅ Created table `{table}`")
            return "created"

        cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        existing_cols = {row["Field"]: row for row in cursor.fetchall()}

        changes = 0
        for col in model.columns:
            if col.name not in existing_cols:
                alter = f"ALTER TABLE `{table}` ADD COLUMN {col.to_sql()}"
                cursor.execute(alter)
                conn.commit()
                print(f"   ➕ `{table}`.`{col.name}` — column added")
                changes += 1
            else:
                db_type = existing_cols[col.name]["Type"].upper()
                model_type = col.col_type.upper()
                if not self._types_match(db_type, model_type):
                    alter = f"ALTER TABLE `{table}` MODIFY COLUMN {col.to_sql()}"
                    try:
                        cursor.execute(alter)
                        conn.commit()
                        print(f"   🔄 `{table}`.`{col.name}` — type changed")
                        changes += 1
                    except Error as e:
                        print(f"   ⚠️  Could not modify `{table}`.`{col.name}`: {e}")

        return "migrated" if changes else "ok"

    @staticmethod
    def _types_match(db_type, model_type):
        return db_type.lower().replace(" ", "") == model_type.lower().replace(" ", "")


def init_database(settings):
    initializer = DatabaseInitializer(settings)
    success = initializer.initialize()
    if not success:
        raise RuntimeError(
            "❌ Database initialization failed. "
            "Check your MySQL credentials in config/config.json."
        )