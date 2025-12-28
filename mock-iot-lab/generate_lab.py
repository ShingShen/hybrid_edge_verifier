import yaml

def generate_docker_compose():
    subnet = "172.25.0.0/16"
    gateway = "172.25.0.1"
    
    services = {}
    
    # Generate 50 DUTs
    for i in range(1, 51):
        service_name = f"dut-{i}"
        ip_address = f"172.25.0.{100 + i}"
        
        services[service_name] = {
            "build": ".",
            "container_name": service_name,
            "hostname": service_name,
            "networks": {
                "iot-net": {
                    "ipv4_address": ip_address
                }
            },
            "restart": "always"
        }

    # Add Test Runner
    services["test-runner"] = {
        "image": "python:3.9-slim",
        "container_name": "test-runner",
        "tty": True,
        "networks": {
            "iot-net": {
                "ipv4_address": "172.25.0.200"
            }
        },
        "command": "sh -c 'pip install pytest paramiko requests telnetlib3 && tail -f /dev/null'"
    }

    compose_config = {
        "version": "3.8",
        "services": services,
        "networks": {
            "iot-net": {
                "driver": "bridge",
                "ipam": {
                    "config": [
                        {
                            "subnet": subnet,
                            "gateway": gateway
                        }
                    ]
                }
            }
        }
    }

    with open("docker-compose.yml", "w") as f:
        # Custom dumper to make it readable, or just standard dump
        yaml.dump(compose_config, f, sort_keys=False, default_flow_style=False)
    
    print("Successfully generated docker-compose.yml with 50 DUTs and 1 Test Runner.")

if __name__ == "__main__":
    generate_docker_compose()
