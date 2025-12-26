from config_manager import ConfigManager
from platforms.base import Platform
from platforms.device_a import DeviceAPlatform
from platforms.device_b import DeviceBPlatform
from platforms.device_c import DeviceCPlatform

import argparse
import os

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

def run_single_device(config, conn_to_run):
    results = []
    platform_instance = None
    device = config.get('device')
    
    print(f"\n--- Begin to test {config.get('ip')} ({device}) ---")

    if device:
        try:
            platform_instance = get_platform_instance(device, config.copy())
        except ValueError as e:
            print(f"[!] Warning: Cannot build the instance of platform for '{device}': {e}")

    # Platform Tests
    if any(t in ['ssh'] for t in conn_to_run):
        if platform_instance:
            if 'ssh' in conn_to_run: 
                results.append(platform_instance.test_ssh_login())
        else:
            msg = f"Do not support '{device}', cannot execute the test of SSH."
            if 'ssh' in conn_to_run: 
                results.append({"name": f"SSH Login Test for {config.get('ip')}", "success": False, "message": msg})
    
    print(f"--- {config.get('ip')} The Tests are finished ---")
    return results

def main():
    parser = argparse.ArgumentParser(description="Hybrid Edge Verifier")
    
    # --- Arguments ---
    parser.add_argument("--device", help="load the special device config")

    # Connection parameters
    parser.add_argument(
        "--conn",
        nargs='+',
        choices=['ssh'],
        help="Choose the connection"
    )

    args = parser.parse_args()

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    base_cm = ConfigManager(config_dir=os.path.join(current_script_dir, "config"))

    conn_to_run = set()
    if args.conn: 
        conn_to_run.update(args.conn)

    try:
        if conn_to_run:
            if args.device:
                base_cm.load_device_config(args.device)
            
            final_config = base_cm.config
            cli_overrides = {k: v for k, v in vars(args).items() if v is not None}
            base_cm._deep_merge(final_config, cli_overrides)
            results = run_single_device(final_config, conn_to_run)
            print(results)
    except KeyboardInterrupt:
        print("\n[*] The execution is stop.\n")
    except Exception as e:
        print(f"[!] Unexpected Error: {e}\n")

if __name__ == "__main__":
    main()