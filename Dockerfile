# Use a stable Python image
FROM python:3.10-slim

# Install important tools
RUN apt-get update &&

# Install Python dependencies
RUN pip install -r requirements.txt