import os
import json


class Config:
    """Application configuration"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Load database config from JSON file
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'configuration.json')

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
            db_config = config_data['databaseConfig']
            server_config = config_data.get('serverConfig', {})  # ← NEW: Load server config
    else:
        # Fallback to default values
        db_config = {
            "user": "root",
            "password": "",
            "host": "127.0.0.1",
            "port": 3306,
            "database": "testing",
            "charset": "utf8mb4",
            "connect_timeout": 10
        }
        server_config = {}  # ← NEW: Empty if no file

    # Database Configuration
    DB_USER = db_config['user']
    DB_PASSWORD = db_config['password']
    DB_HOST = db_config['host']
    DB_PORT = db_config['port']
    DB_NAME = db_config['database']
    DB_CHARSET = db_config.get('charset', 'utf8mb4')
    DB_CONNECT_TIMEOUT = db_config.get('connect_timeout', 10)

    # Security
    SECRET_KEY = "localhost123"

    # Server Configuration ← MODIFIED: Load from JSON
    SERVER_HOST = server_config.get('host', '0.0.0.0')
    SERVER_PORT = server_config.get('port', 5004)
    DEBUG = server_config.get('debug', True)

    # SSL Configuration ← MODIFIED: Load from JSON
    SSL_CERT = os.path.join(BASE_DIR, server_config.get('ssl_cert', 'cert.pem'))
    SSL_KEY = os.path.join(BASE_DIR, server_config.get('ssl_key', 'Key.pem'))