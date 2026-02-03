import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config



class Database:
    """Database connection manager"""

    _connection = None

    @staticmethod
    def get_connection():
        """Get database connection (singleton pattern)"""
        if Database._connection is None or not Database._connection.is_connected():
            try:
                Database._connection = mysql.connector.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    charset=Config.DB_CHARSET,
                    autocommit=True,
                    use_unicode=True,
                    connect_timeout=Config.DB_CONNECT_TIMEOUT,
                    auth_plugin='mysql_native_password'
                )
                print("✅ Database connected successfully")
            except Error as e:
                print(f"❌ Database connection error: {e}")
                raise e

        return Database._connection

    @staticmethod
    def execute_query(query, params=None, fetch=True):
        """Execute a query and return results"""
        connection = Database.get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.lastrowid

        except Error as e:
            print(f"❌ Query error: {e}")
            raise e
        finally:
            cursor.close()

    @staticmethod
    def close_connection():
        """Close database connection"""
        if Database._connection and Database._connection.is_connected():
            Database._connection.close()
            print("✅ Database connection closed")