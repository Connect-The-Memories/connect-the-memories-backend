# Use an official Python runtime as base image
FROM python:3.13.3-slim

ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (leverage Docker caching)
COPY requirements.txt ./

# Install dependencies.
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY . ./

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Use Gunicorn for better performance
CMD exec gunicorn --bind "0.0.0.0:$PORT" --workers 1 --threads 1 --timeout 0 app:app