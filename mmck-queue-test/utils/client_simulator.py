import socket
import json
import time
import threading
import random

HOST = '127.0.0.1'
PORT = 8080

def send_request(source_id, source_type):
    """
    Simulates a single client (SSH/HTTP) sending a request.
    """
    request_data = {
        "source": f"{source_type}_{source_id}",
        "command": "heavy_calc",
        "params": [random.random() * 100 for _ in range(50)]
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((HOST, PORT))
            s.sendall(json.dumps(request_data).encode('utf-8'))
            
            response = s.recv(1024)
            response_json = json.loads(response.decode('utf-8'))
            
            if response_json.get("status") == "Rejected":
                print(f"[{source_type}] Request BLOCKED (System Protected)")
            else:
                print(f"[{source_type}] Request Accepted")
                
    except Exception as e:
        print(f"[{source_type}] Connection Error: {e}")

def run_simulation(n_requests, delay):
    threads = []
    print(f"Starting simulation: {n_requests} requests...")
    
    for i in range(n_requests):
        # Randomly simulate different sources
        src_type = random.choice(["SSH", "HTTP"])
        t = threading.Thread(target=send_request, args=(i, src_type))
        threads.append(t)
        t.start()
        time.sleep(delay) # Inter-arrival time

    for t in threads:
        t.join()

if __name__ == "__main__":
    # Simulate a burst of 50 requests in a very short time (0.01s interval)
    # This should trigger the M/M/c/K protection mechanism.
    run_simulation(50, 0.01)