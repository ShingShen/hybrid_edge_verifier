FROM python:3.10-slim

# Install important tools
RUN apt-get update && \
    apt-get install -y openssh-client sshpass expect && \
    cd /tmp && \
    rm -rf /tmp/*

# Set the working directory
WORKDIR /usr/src/app

# Copy the rest of the application's source code
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Default command to show help
CMD ["python", "main.py", "--help"]
