# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . /app

# Install dependencies (with verbosity)
RUN pip install --no-cache-dir -r requirements.txt -v

# Expose port 5000
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
