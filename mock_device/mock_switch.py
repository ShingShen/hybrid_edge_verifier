import http.server
import socketserver
import json
import argparse
import time

class SwitchHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    A simple HTTP request handler to simulate a network switch's API.
    """
    model_name = "VirtualSwitch"
    firmware_version = "1.0.0"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        response = {}
        if self.path == '/':
            response = {"message": f"Welcome to {self.model_name} simulator!"}
        elif self.path == '/api/system/info':
            response = {
                "model": self.model_name,
                "firmware": self.firmware_version,
                "uptime": time.time() - self.server.start_time
            }
        else:
            self.send_error(404, "Not Found")
            return
            
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/login':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "success", "token": "dummy-token-12345"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

def run_server(port, model, version):
    Handler = SwitchHttpRequestHandler
    Handler.model_name = model
    Handler.firmware_version = version

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.start_time = time.time()
        print(f"Serving Virtual Switch '{model}' on port {port}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()
            print(f"\nVirtual Switch on port {port} stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtual Switch Simulator")
    parser.add_argument("--port", type=int, required=True, help="Port to run the server on.")
    parser.add_argument("--model", default="VirtualSwitch", help="Model name to simulate.")
    parser.add_argument("--version", default="1.0.0", help="Firmware version to simulate.")
    args = parser.parse_args()
    
    run_server(args.port, args.model, args.version)
