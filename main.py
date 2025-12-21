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

    # Connection parameters
    parser.add_argument(
        "--connection",
        choices=[
            'http','ssh', 'telnet', 'serial'
        ]
    )

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
    else:
        print("[*] Do not assign device.")

    results = []
    connection_to_run = set()
    if args.connection:
        connection_to_run.update(args.connection)

    platform_instance = None
    if args.device:
        try:
            platform_instance = get_platform_instance(args.device, cm.config.copy())
        except ValueError as e:
            print(f"[!] Error: Cannot  build platform instance - {e}.")
            platform_instance = None

    try:
        if connection_to_run:
            if 'http' in connection_to_run:
                if platform_instance:
                    results.append(platform_instance.http_connection())
    except KeyboardInterrupt:
        print("\n[*] The execution is stop.\n")
    except Exception as e:
        print(f"[!] Unexpected Error: {e}\n")

if __name__ == "__main__":
    main()