from .base import Platform

class DeviceAPlatform(Platform):
    def ssh_connection(self):
        return super().ssh_connection()
    
    def telnet_connection(self):
        return super().telnet_connection()
    
    def serial_connection(self):
        return super().serial_connection()