"""
Configuration loader and validator
"""
import json
import os


class Settings:
    """Manages application configuration"""

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def _validate_config(self):
        """Validate required configuration fields"""
        required_sections = ['credentials', 'api', 'sync', 'database']

        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")

        # Validate credentials
        if not self.config['credentials'].get('username'):
            raise ValueError("Username is required in credentials")
        if not self.config['credentials'].get('password'):
            raise ValueError("Password is required in credentials")

        print("✅ Configuration loaded and validated successfully")

    def save_config(self):
        """Save configuration back to file (used for token updates)"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Configuration saved successfully")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            raise

    # Easy access properties
    @property
    def username(self):
        return self.config['credentials']['username']

    @property
    def password(self):
        return self.config['credentials']['password']

    @property
    def api_base_url(self):
        return self.config['api']['base_url']

    @property
    def login_url(self):
        return f"{self.api_base_url}{self.config['api']['login_endpoint']}"

    @property
    def whats_new_url(self):
        return f"{self.api_base_url}{self.config['api']['whats_new_endpoint']}"

    @property
    def api_timeout(self):
        return self.config['api'].get('timeout', 30)

    @property
    def sync_interval_minutes(self):
        return self.config['sync']['interval_minutes']

    @property
    def sync_status_file(self):
        return self.config['sync']['status_file']

    @property
    def token_refresh_interval_minutes(self):
        return self.config['sync']['token_refresh_interval_minutes']

    @property
    def database_config(self):
        return self.config['database']

    @property
    def network_check_url(self):
        return self.config['network']['check_url']

    @property
    def network_check_timeout(self):
        return self.config['network']['check_timeout']

    def get_token(self):
        """Get current token from config"""
        return self.config.get('token')

    def set_token(self, token):
        """Update token in memory and save to file"""
        self.config['token'] = token
        self.save_config()
        print(f"✅ Token updated and saved")


# Singleton instance
_settings_instance = None

def get_settings(config_path="config.json"):
    """Get or create settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings(config_path)
    return _settings_instance