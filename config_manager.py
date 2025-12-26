import os
import yaml

class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.config = {}
        # self.load_device_config("")

    def load_device_config(self, device_name):
        device_config_path = os.path.join(self.config_dir, "", f"{device_name}.yaml")
        if not os.path.exists(device_config_path):
            raise FileNotFoundError(f"Device configuration file not found: {device_config_path}")

        with open(device_config_path, 'r', encoding='utf-8') as f:
            device_config = yaml.safe_load(f)

        return self._deep_merge(self.config, device_config)

    def _deep_merge(self, default_dict, custom_dict):
        for key, value in custom_dict.items():
            if isinstance(value, dict) and key in default_dict and isinstance(default_dict[key], dict):
                default_dict[key] = self._deep_merge(default_dict[key], value)
            else:
                default_dict[key] = value
        return default_dict