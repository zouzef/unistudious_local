import sys
import os
import mysql.connector

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def check_user(username, password):
    """Check if tablet user credentials are valid"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            autocommit=True
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                id,
                name,
                mac_id as mac,
                password,
                status,
                room_id as roomId
            FROM tablet 
            WHERE mac_id = %s AND password = %s
        """, (username, password))

        rows = cursor.fetchone()

        cursor.close()
        conn.close()

        return rows is not None

    except Exception as e:
        print(f"Error in check_user: {e}")
        return False


def check_slc(mac, password):
    """Check if SLC device credentials are valid"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            autocommit=True
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM special_table 
            WHERE mac_slc = %s AND pass = %s
        """, (mac, password))

        rows = cursor.fetchone()

        cursor.close()
        conn.close()

        return rows is not None

    except Exception as e:
        print(f"Error in check_slc: {e}")
        return False