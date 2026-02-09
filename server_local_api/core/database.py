import mysql.connector
from mysql.connector import Error, pooling
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class Database:
    """Database connection manager with connection pooling"""

    _connection_pool = None

    @staticmethod
    def get_pool():
        """Get or create connection pool"""
        if Database._connection_pool is None:
            try:
                Database._connection_pool = pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=32,
                    pool_reset_session=True,
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
                print("✅ Database connection pool created successfully")
            except Error as e:
                print(f"❌ Database pool creation error: {e}")
                raise e

        return Database._connection_pool

    @staticmethod
    def execute_query(query, params=None, fetch=True):
        """Execute a query and return results"""
        pool = Database.get_pool()
        connection = None
        cursor = None

        try:
            connection = pool.get_connection()
            connection.ping(reconnect=True)

            cursor = connection.cursor(dictionary=True)
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
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if connection:  # ← MOVED INSIDE finally block, same indent as "if cursor:"
                try:
                    connection.close()
                except:
                    pass