from abc import ABC, abstractmethod
from utils.ssh_docker_helper import run_ssh_command_with_expect

class Platform(ABC):
    def __init__(self, config):
        self.config = config
        self.ip = config.get('ip')
        self.user = config.get('user')
        self.password = config.get('password')

    # @abstractmethod
    # def http_connection(self):
    #     pass

    # @abstractmethod
    # def ssh_connection(self):
    #     pass

    # @abstractmethod
    # def telnet_connection(self):
    #     pass

    # @abstractmethod
    # def serial_connection(self):
    #     pass

    def _run_ssh_command(self, command: str) -> tuple[bool, str]:
        return run_ssh_command_with_expect(self.config, command)
    
    def test_ssh_login(self) -> dict:
        test_name = "SSH Login Test"
        success, message = self._run_ssh_command("echo 'SSH Login Success'")

        if success:
            return {"name": test_name, "success": True, "message": "SSH Login Success。"}
        else:
            return {"name": test_name, "success": False, "message": f"SSH Login Fail. Message:\n{message}"}
