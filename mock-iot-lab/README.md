# Mock IoT Lab

This project simulates a lab of 50+ Linux IoT devices using lightweight Docker containers based on Alpine Linux.

## Features per Device (DUT)

*   **SSH (Port 22)**: User: `root`, Password: `password`
*   **Telnet (Port 23)**: User: `root`, Password: `password`
*   **HTTP (Port 80)**: Returns JSON status `{"status": "online"}`
*   **Serial over TCP (Port 9000)**: Raw shell access simulating a serial console.
*   **Simulation**: Custom MOTD banner and hijacked `uname -a` to mimic a specific Debian ARM device.

## Prerequisites

*   Docker
*   Docker Compose
*   Python 3 (to generate the configuration)
*   `pip install pyyaml` (required for the generator script)

## Quick Start

1.  **Generate Configuration**:
    Run the Python script to create the `docker-compose.yml` file.
    ```bash
    python3 generate_lab.py
    ```

2.  **Build and Start the Lab**:
    ```bash
    docker compose up -d --build
    ```

3.  **Access Devices**:
    *   DUTs are available at IPs `172.25.0.101` through `172.25.0.150`.
    *   Example SSH: `ssh root@172.25.0.101`
    *   Example HTTP: `curl http://172.25.0.101`

4.  **Run Tests**:
    A `test-runner` container is included in the network at `172.25.0.200`.
    
    Enter the test runner:
    ```bash
    docker exec -it test-runner bash
    ```
    
    From here, you can run connectivity tests against the DUTs.
    ```bash
    # Example: Check connection to dut-1
    ping -c 2 172.25.0.101
    ```

## Cleanup

To stop and remove all containers and network:
```bash
docker compose down
```

## Note

To delete old SSH connection record:
Ex.
```bash
ssh-keygen -f "/.ssh/known_hosts" -R "172.25.0.150"
```
