from config_manager import ConfigManager
from platforms.base import Platform
from platforms.device_a import DeviceAPlatform
from platforms.device_b import DeviceBPlatform
from platforms.device_c import DeviceCPlatform

import argparse
import os
import sys

def get_platform_instance(device_name: str, config: dict) -> Platform:
    platform_map = {
        "device_a": DeviceAPlatform,
        "device_b": DeviceBPlatform,
        "device_c": DeviceCPlatform
    }
    platform_class = platform_map.get(device_name)
    if not platform_class:
        raise ValueError(f"Do not support '{device_name}'. Please check the  instance of platforms' instances")
    return platform_class(config)

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--device", help="load the special device config")

    args = parser.parse_args()

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    cm = ConfigManager(config_dir=os.path.join(current_script_dir, "config"))

    if args.device:
        try:
            cm.load_device_config(args.model)
            print(f"[*] Loaded the device '{args.model}' config")
        except FileNotFoundError as e:
            print(f"[!] Error: {e}")
            sys.exit(1)
if __name__ == "__main__":
    main()