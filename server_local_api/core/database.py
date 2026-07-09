import mysql.connector
from mysql.connector import Error, pooling
import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class Database:
	"""Database connection manager with connection pooling"""

	_connection_pool = None
	_pool_lock = threading.Lock()  # ← ADD THIS: Thread-safe singleton

	@staticmethod
	def get_pool():
		"""Get or create connection pool (thread-safe singleton)"""
		if Database._connection_pool is None:
			with Database._pool_lock:  # ← ADD THIS: Lock to prevent race conditions
				# Double-check inside the lock
				if Database._connection_pool is None:
					try:
						Database._connection_pool = pooling.MySQLConnectionPool(
							pool_name="mypool",
							pool_size=10,  # ← REDUCE THIS: Start with smaller pool
							pool_reset_session=True,
							host=Config.DB_HOST,
							port=Config.DB_PORT,
							user=Config.DB_USER,
							password=Config.DB_PASSWORD,
							database=Config.DB_NAME,
							charset=Config.DB_CHARSET,
							autocommit=False,
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
		"""
        Execute a query and return results
        - For SELECT queries: set fetch=True (returns rows)
        - For INSERT/UPDATE/DELETE: set fetch=False (returns affected rows or lastrowid)
        """
		pool = Database.get_pool()
		connection = None
		cursor = None

		try:
			connection = pool.get_connection()

			if connection.is_connected():
				cursor = connection.cursor(dictionary=True)
				cursor.execute(query, params or ())

				if fetch:
					result = cursor.fetchall()
					return result
				else:
					connection.commit()

					if cursor.lastrowid > 0:
						return cursor.lastrowid
					else:
						return cursor.rowcount

		except Error as e:
			print(f"❌ Query error: {e}")
			if connection:
				connection.rollback()
			raise e

		finally:
			if cursor:
				try:
					cursor.close()
				except Exception as e:
					print(f"Error closing cursor: {e}")

			if connection:
				try:
					connection.close()
				except Exception as e:
					print(f"Error closing connection: {e}")

	@staticmethod
	def fetch_all(query, params=None):
		"""Fetch all rows from a SELECT query"""
		return Database.execute_query(query, params, fetch=True)

	@staticmethod
	def fetch_one(query, params=None):
		"""Fetch one row from a SELECT query"""
		result = Database.execute_query(query, params, fetch=True)
		return result[0] if result else None

	@staticmethod
	def insert(query, params=None):
		"""Execute INSERT and return last inserted ID"""
		return Database.execute_query(query, params, fetch=False)

	@staticmethod
	def update(query, params=None):
		"""Execute UPDATE and return number of affected rows"""
		return Database.execute_query(query, params, fetch=False)

	@staticmethod
	def delete(query, params=None):
		"""Execute DELETE and return number of affected rows"""
		return Database.execute_query(query, params, fetch=False)

	@staticmethod
	def execute_transaction(queries):
		"""
		Execute multiple queries in a single transaction.
		- queries: list of (query, params) tuples
		- Commits once at the end if all succeed
		- Rolls back everything if any query fails
		- Returns a list of results, one per query:
			- for SELECT: list of rows
			- for INSERT/UPDATE/DELETE: lastrowid or rowcount
		"""
		pool = Database.get_pool()
		connection = None
		cursor = None

		try:
			connection = pool.get_connection()
			cursor = connection.cursor(dictionary=True)

			results = []
			for query, params in queries:
				cursor.execute(query, params or ())

				if query.strip().upper().startswith("SELECT"):
					results.append(cursor.fetchall())
				else:
					if cursor.lastrowid > 0:
						results.append(cursor.lastrowid)
					else:
						results.append(cursor.rowcount)

			connection.commit()
			return results

		except Error as e:
			print(f"❌ Transaction error: {e}")
			if connection:
				connection.rollback()
			raise e

		finally:
			if cursor:
				try:
					cursor.close()
				except Exception as e:
					print(f"Error closing cursor: {e}")
			if connection:
				try:
					connection.close()
				except Exception as e:
					print(f"Error closing connection: {e}")
