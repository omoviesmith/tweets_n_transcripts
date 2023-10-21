# syntax=docker/dockerfile:1

# Using official python runtime base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port for the Flask app to run
EXPOSE 5000

# Run gunicorn when the container launches
CMD ["gunicorn", "-t", "300","--bind", "0.0.0.0:5000", "app:app"]