Document Retrieval and Chat API with Cohere
This project is an API-based application for storing documents and retrieving relevant documents using the Cohere AI embeddings API. It also supports searching for similar documents using cosine similarity and provides a chat interface based on the stored documents.

Features
Store documents and generate embeddings using Cohere.
Search for similar documents based on input text.
Rate limiting for API users.
Chat interface using stored documents as context.
Uses SQLite as the primary database.
Caches search results using Redis for faster lookups.
Requirements
Python 3.7+
Cohere API Key
Redis
SQLite (default database)
Installation
Step 1: Clone the Repository

git clone <repository-url>
cd docrag
Step 2: Create and Activate a Virtual Environment

python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
Step 3: Install Required Packages

pip install -r requirements.txt

Step 4: Set Up Redis
Install and run Redis locally or use a remote Redis instance. You can download Redis from the official site: https://redis.io/

If running Redis locally, start it with the following command:

redis-server

Step 5: Set Up Cohere API Key
Create a .env file in the project root directory and add your Cohere API key:
COHERE_API_KEY=your_cohere_api_key_here

Alternatively, you can replace the following line in app.py with your API key directly:
co = cohere.Client('your_api_key')

Step 6: Set Up SQLite Database
The database is automatically created when you run the app. However, you can also manually initialize the SQLite database by running the Python shell:


In the Python shell, run:


from app import create_table
create_table()
This will create the necessary documents and users tables.

Step 7: Running the Application
Run the Flask application:
flask run
This will start the API server on http://localhost:5000.

Step 8: Using Docker (Optional)
You can run the application via Docker for easier environment setup. Here’s how:

Build the Docker image:
docker build -t docrag-app .

Run the Docker container:
docker run -d -p 5000:5000 --name docrag-container docrag-app
The API will be available at http://localhost:5000.

API Endpoints
1. Health Check
Endpoint: /health
Method: GET

Checks if the API is running.

Response:

json
Copy code
{
  "status": "API is running"
}

2. Store a Document
Endpoint: /store
Method: POST
Description: Stores a document and its embedding in the database.

Request Body:


{
  "text": "This is a sample document."
}
Response:


{
  "message": "Document stored successfully",
  "document_id": 3
}

3. Search for Similar Documents
Endpoint: /search
Method: POST
Description: Search for similar documents based on the provided input text.

Request Body:


{
  "user_id": "user123",
  "text": "Sample search text",
  "top_k": 5,
  "threshold": 0.1
}
top_k: The number of similar documents to return (default: 5).
threshold: Minimum cosine similarity score (default: 0.1).

Response:

{
  "inference_time": 0.034,
  "results": [
    {
      "document_id": 1,
      "text": "Document text 1",
      "similarity": 0.89
    },
    {
      "document_id": 2,
      "text": "Document text 2",
      "similarity": 0.72
    }
  ]
}

4. Chat with AI Using Documents as Context
Endpoint: /chat
Method: POST
Description: Chat with AI based on the stored documents. AI generates a response considering the context of the most relevant documents.

Request Body:
{
  "user_id": "user123",
  "message": "How does AI work?",
  "top_k": 5
}
Response:
{
  "message": "AI works by..."
}
Rate Limiting
Users are limited to 5 requests per day. This is managed by the users table in the SQLite database.

If a user exceeds the limit, the API will return a 429 Too Many Requests response:
{
  "error": "API rate limit exceeded"
}

Caching with Redis
The application uses Redis to cache the results of searches for 1 hour. If a search query is repeated within that hour, the results are returned from the cache, reducing the need for recalculating embeddings.

Background Tasks
A background task resets the request count for all users every 24 hours. This is implemented using Python’s threading module.

Troubleshooting

Common Errors
sqlite3.OperationalError: database is locked

This can occur if there are multiple connections trying to access the SQLite database simultaneously.
Solution: Use the timeout option when connecting to SQLite or consider upgrading to a more robust database like PostgreSQL or MySQL.
Redis Connection Error

If you see redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused, make sure Redis is running on the specified host and port.
Solution: Start Redis locally or adjust the Redis configuration in app.py if using a remote Redis instance.
Cohere API Errors

If the API fails to generate embeddings or responses, ensure your Cohere API key is valid and you have enough credits.
Using SQLite in Threaded Environments
SQLite is not well-suited for highly concurrent environments. If you face concurrency issues, you can:

Increase the timeout (timeout=10) when connecting to the database.
Use check_same_thread=False if your app is using threads.
Future Improvements
Move to a Production-Grade Database:
Consider using PostgreSQL or MySQL for better performance and concurrency management.

Implement More Robust Caching:
Currently, only search queries are cached. Chat responses and document embeddings could also be cached for efficiency.

Authentication and Security:
Implement authentication (e.g., using API keys) to secure the API and prevent abuse.

Front-end Integration:
Build a front-end interface for interacting with the API more easily.

License
This project is licensed under the MIT License.

Contributions
Feel free to open issues or submit pull requests to contribute to the project.

Contact
For questions or support, please contact [your-email@example.com].

