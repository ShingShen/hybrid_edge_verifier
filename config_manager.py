import os
import yaml

class ConfigManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.load_device_config()

    def load_device_config(device_name):
        device_config_path = os.path.join(f"{device_name}.yaml")
        if not os.path.exists(device_config_path):
            raise FileNotFoundError(f"Device configuration file not found: {device_config_path}")

        with open(device_config_path, 'r', encoding='utf-8') as f:
            device_config = yaml.safe_load(f)

        return device_config