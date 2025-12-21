from abc import ABC, abstractmethod

class Platform(ABC):
    def __init__(self, config):
        self.config = config
        self.user = config.get('user')
        self.password = config.get('password')

    @abstractmethod
    def http_connection(self):
        pass

    @abstractmethod
    def ssh_connection(self):
        pass

    @abstractmethod
    def telnet_connection(self):
        pass

    @abstractmethod
    def serial_connection(self):
        pass
