#!/bin/bash

# Generate SSH Host Keys if they don't exist
ssh-keygen -A

# Start SSH Daemon
/usr/sbin/sshd

# Start Telnet Daemon (busybox-extras)
# -F: Foreground (we background it manually)
# -p: Port
# -l: Login program
# -b: Bind address (ensure IPv4)
telnetd -p 23 -l /bin/login -b 0.0.0.0 &

# Start Nginx
nginx

# Start Socat for Serial over TCP (Port 9000)
# Simulates a shell on port 9000
socat TCP-LISTEN:9000,fork,reuseaddr EXEC:"/bin/bash -l",pty,stderr,setsid,sigint,sane &

# Keep container running
tail -f /dev/null
