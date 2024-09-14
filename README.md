Document Retrieval System
Overview
This document retrieval system is designed to support chat applications by providing relevant context from stored documents. It includes endpoints for storing documents, searching for documents based on user queries, and interacting with a chat service that uses the retrieved documents as context. The system features caching, rate-limiting, and background tasks for enhanced performance and reliability.

Features
Health Check Endpoint: Verify if the API is running.
Store Document Endpoint: Store documents and their embeddings.
Search Endpoint: Search for documents based on a query with caching and rate-limiting.
Chat Endpoint: Generate responses using stored document context.
Background Task: Reset user request counts daily.
Setup
Prerequisites
Python 3.11+
Redis: Ensure Redis is installed and running on localhost:6379.
Cohere API Key: Obtain an API key from Cohere.
Installation
Clone the Repository


Copy code
git clone <repository_url>
cd <repository_directory>
Install Dependencies

Create a requirements.txt file with the following content:

flask
cohere
numpy
redis
Install the dependencies:


pip install -r requirements.txt
Set Up the Database

The SQLite database will be created automatically when you run the application for the first time. It includes tables for documents and user tracking.

Configure Environment Variables

Replace 'YOUR_COHERE_API_KEY' in the app.py file with your actual Cohere API key.

Docker Setup
Create a Dockerfile

Use the following Dockerfile to build and run the application in a container:

Dockerfile
Copy code
# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
Build and Run the Docker Container


docker build -t document-retrieval-app .
docker run -p 5000:5000 document-retrieval-app
API Endpoints
Health Check
Endpoint: /health
Method: GET
Response: { "status": "API is running" }
--------------------
Store Document
Endpoint: /store
Method: POST
Request Body:


{
    "text": "Your document text here"
}
Response:



{
    "message": "Document stored successfully",
    "document_id": 1
}
---------------------
Search
Endpoint: /search
Method: POST
Request Body:

{
    "user_id": "user_123",
    "text": "Query text",
    "top_k": 5,
    "threshold": 0.1
}
Response:


{
    "inference_time": 0.123,
    "results": [
        {
            "document_id": 1,
            "text": "Document text",
            "similarity": 0.95
        }
    ]
}

------------------------------
Chat
Endpoint: /chat
Method: POST
Request Body:

json
Copy code
{
    "user_id": "user_123",
    "message": "User message",
    "top_k": 5
}
Response:


{
    "
    message": "AI response based on context"
}


Caching Strategy
Redis Cache: Used for caching search results to improve performance and reduce response time.
Cache Expiration: Cached results are stored for 1 hour to balance performance and data freshness.
Rate Limiting
User Requests: Users are limited to 5 requests per day. Exceeding this limit results in a 429 Too Many Requests response.
Background Tasks
Request Count Reset: User request counts are reset daily to ensure fair usage. This is handled by a background thread.
Logging
Error Logging: Logs are recorded for API errors and issues for troubleshooting and monitoring.
Contribution
Feel free to contribute by submitting issues or pull requests. Ensure that all code follows best practices and is well-documented.

License
This project is licensed under the MIT License. See the LICENSE file for details.