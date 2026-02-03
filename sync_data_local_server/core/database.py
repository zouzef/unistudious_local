"""
Database handler for local MySQL database
Manages connection and basic operations
"""
import mysql.connector
from mysql.connector import Error


class Database:
    """Handles MySQL database connection and operations"""

    def __init__(self, settings):
        """
        Initialize Database handler

        Args:
            settings: Settings instance with database configuration
        """
        self.settings = settings
        self.db_config = settings.database_config
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Connect to MySQL database

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print(f"🔌 Connecting to MySQL database: {self.db_config['database']}")

            self.connection = mysql.connector.connect(
                host=self.db_config['host'],
                port=self.db_config.get('port', 3306),
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                db_info = self.connection.get_server_info()
                print(f"✅ Connected to MySQL Server version {db_info}")

                # Get current database name
                self.cursor.execute("SELECT DATABASE();")
                record = self.cursor.fetchone()
                print(f"✅ Connected to database: {record['DATABASE()']}")

                return True

        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("✅ MySQL connection closed")
        except Error as e:
            print(f"❌ Error closing connection: {e}")

    def execute_query(self, query, params=None):
        """
        Execute a SQL query (INSERT, UPDATE, DELETE)

        Args:
            query: SQL query string
            params: Query parameters (tuple)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            self.connection.commit()
            print(f"✅ Query executed successfully")
            return True

        except Error as e:
            print(f"❌ Query execution error: {e}")
            return False

    def fetch_query(self, query, params=None):
        """
        Execute a SELECT query and fetch results

        Args:
            query: SQL query string
            params: Query parameters (tuple)

        Returns:
            list: Query results as list of dictionaries
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            return results

        except Error as e:
            print(f"❌ Query fetch error: {e}")
            return []

    def test_connection(self):
        """Test database connection and show tables"""
        if self.connect():
            try:
                # Show all tables
                self.cursor.execute("SHOW TABLES")
                tables = self.cursor.fetchall()

                if tables:
                    print(f"\n📊 Tables in database:")
                    for table in tables:
                        table_name = list(table.values())[0]
                        print(f"  - {table_name}")
                else:
                    print("\n⚠️  No tables found in database")

                return True
            except Error as e:
                print(f"❌ Error: {e}")
                return False
            finally:
                self.disconnect()
        return False

