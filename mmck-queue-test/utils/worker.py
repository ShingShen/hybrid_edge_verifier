import sys
import json
import time
import math

def perform_task(command, params):
    """
    Executes the actual heavy calculation.
    """
    # Simulate CPU-bound work
    # In a real scenario, this would be data processing, image recognition, etc.
    if command == "heavy_calc":
        # Simulate processing time (e.g., 100ms)
        time.sleep(0.1) 
        result = sum(math.sqrt(x) for x in params)
        return {"result": result, "processed_items": len(params)}
    
    elif command == "serial_write":
        # Simulate writing to a serial port
        time.sleep(0.05)
        return {"result": "Written to /dev/ttyUSB0", "bytes": len(params)}
    
    else:
        return {"error": "Unknown command"}

if __name__ == "__main__":
    try:
        # Rust passes arguments: [script_name, command, json_params]
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing arguments"}))
            sys.exit(1)

        cmd = sys.argv[1]
        raw_params = sys.argv[2]
        params = json.loads(raw_params)
        
        # Execute logic
        output = perform_task(cmd, params)

        # Print result to stdout (Rust captures this)
        print(json.dumps(output))

    except Exception as e:
        # Print errors to stderr (Rust captures this as error log)
        sys.stderr.write(str(e))
        sys.exit(1)