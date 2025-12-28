FROM alpine:latest

# Install services
# openssh: for SSH
# busybox-extras: for Telnet
# nginx: for HTTP
# socat: for Serial over TCP
# bash: shell
RUN apk add --no-cache openssh busybox-extras nginx socat bash

# Configure Users
# Set root password to "password"
RUN echo "root:password" | chpasswd

# Configure SSH
# Allow root login
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#Banner.*/Banner \/etc\/issue.net/' /etc/ssh/sshd_config

# Configure MOTD and Banner
COPY motd_content.txt /etc/motd
COPY motd_content.txt /etc/issue.net

# Allow root login on Telnet (remove securetty)
RUN rm -f /etc/securetty

# Mock uname
# We move the real busybox uname if it exists as a symlink, or just shadow it in /usr/local/bin
RUN echo '#!/bin/bash' > /usr/local/bin/uname && \
    echo 'if [[ "$1" == "-a" ]]; then' >> /usr/local/bin/uname && \
    echo '  echo "Linux iot-device 4.14.98-v7 #1 SMP Tue Oct 1 14:47:58 CST 2019 armv7l"' >> /usr/local/bin/uname && \
    echo 'else' >> /usr/local/bin/uname && \
    echo '  /bin/uname "$@"' >> /usr/local/bin/uname && \
    echo 'fi' >> /usr/local/bin/uname && \
    chmod +x /usr/local/bin/uname

# Configure Nginx
RUN mkdir -p /run/nginx
RUN echo 'server { listen 80; location / { return 200 "{\"status\": \"online\"}"; add_header Content-Type application/json; } }' > /etc/nginx/http.d/default.conf

# Setup Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose Ports
EXPOSE 22 23 80 9000

ENTRYPOINT ["/entrypoint.sh"]

