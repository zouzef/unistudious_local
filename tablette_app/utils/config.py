"""Configuration management utilities."""
import json


def load_config():
    """Load configuration from JSON file."""
    with open("tablet_configuration.json", "r") as f:
        return json.load(f)


# Global config instance
config = load_config()