import cohere
import sqlite3
import numpy as np
import pickle
import time
import threading
import logging
from flask import Flask, request, jsonify
from redis import Redis

app = Flask(__name__)

# Initialize Cohere API client with your API key
co = cohere.Client('wvVOr2okWTUHAHq7iCHuVZ9FxhUexUL39JvqwrfC')

# Redis cache setup
cache = Redis(host='localhost', port=6379, db=0)
# cache = Redis(host='redis-container', port=6379, db=0)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to SQLite database (or create it if it doesn't exist)
def get_db_connection():
    conn = sqlite3.connect('documents.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the documents table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            request_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


# Function to store a document and its embedding in the database
def store_document(text, embedding):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert the embedding (list of floats) to a binary format using pickle
    embedding_blob = pickle.dumps(embedding)

    # Insert the document and embedding into the table, SQLite will auto-increment the document_id
    cursor.execute(
        "INSERT INTO documents (text, embedding) VALUES (?, ?)",
        (text, embedding_blob)
    )
    conn.commit()
    
    # Get the auto-generated document_id
    doc_id = cursor.lastrowid
    conn.close()

    return doc_id

# Function to retrieve all stored documents and their embeddings
def get_all_documents_with_embeddings():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all documents and their embeddings from the table
    cursor.execute("SELECT document_id, text, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()

    documents = []
    for row in rows:
        # Convert the binary embedding back to a list of floats using pickle
        embedding = pickle.loads(row['embedding'])
        documents.append({
            'document_id': row['document_id'],
            'text': row['text'],
            'embedding': embedding
        })

    return documents

# Function to compute cosine similarity
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Function to update or create a user record
def update_user_request_count(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT request_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        request_count = row['request_count']
        if request_count >= 5:
            return False
        cursor.execute("UPDATE users SET request_count = ? WHERE user_id = ?", (request_count + 1, user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, request_count) VALUES (?, ?)", (user_id, 1))

    conn.commit()
    conn.close()
    return True

# Function to reset user request count periodically
def reset_user_request_counts():
    while True:
        time.sleep(24 * 3600)  # Reset every 24 hours
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET request_count = 0")
        conn.commit()
        conn.close()

# Health endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "API is running"}), 200

@app.route("/store", methods=["POST"])
def store():
    """
    Endpoint to store a document in the database along with its embedding.
    """
    data = request.get_json()
    document_text = data.get("text", "")
    if not document_text:
        return jsonify({"error": "Document text is required"}), 400

    # Generate embedding for the document using Cohere API
    try:
        embedding_response = co.embed(texts=[document_text])
        embedding = embedding_response.embeddings[0]
    except Exception as e:
        logger.error(f"Cohere API embedding failed: {str(e)}")
        return jsonify({"error": f"Cohere API embedding failed: {str(e)}"}), 500

    # Store document and its embedding in the database
    doc_id = store_document(document_text, embedding)

    return jsonify({"message": "Document stored successfully", "document_id": doc_id})


# Search endpoint
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    user_id = data.get('user_id')
    prompt_text = data.get('text')
    top_k = data.get('top_k', 5)
    threshold = data.get('threshold', 0.1)
    start_time = time.time()

    if not user_id or not prompt_text:
        return jsonify({"error": "User ID and search text are required"}), 400

    if not update_user_request_count(user_id):
        return jsonify({"error": "API rate limit exceeded"}), 429

    # Generate embedding for the search query
    try:
        prompt_embedding_response = co.embed(texts=[prompt_text])
        prompt_embedding = prompt_embedding_response.embeddings[0]
    except Exception as e:
        logger.error(f"Cohere API embedding failed: {str(e)}")
        return jsonify({"error": f"Cohere API embedding failed: {str(e)}"}), 500

    # Check cache first
    cache_key = f"search_{prompt_text}_{top_k}_{threshold}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return jsonify({
            "inference_time": 0,
            "results": pickle.loads(cached_result)
        })

    # Retrieve all stored documents and embeddings
    documents = get_all_documents_with_embeddings()

    # Calculate similarity between the query embedding and document embeddings
    results = []
    for doc in documents:
        similarity = cosine_similarity(prompt_embedding, doc['embedding'])
        if similarity > threshold:
            results.append({
                "document_id": doc['document_id'],
                "text": doc['text'],
                "similarity": similarity
            })

    # Sort the results by similarity and take top_k
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]

    # Cache the result
    cache.set(cache_key, pickle.dumps(results), ex=3600)  # Cache for 1 hour

    # Record the inference time for logging
    inference_time = time.time() - start_time

    return jsonify({
        "inference_time": inference_time,
        "results": results
    })

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('message')
    top_k = data.get('top_k', 5)  # Number of documents to consider for context

    if not user_id or not user_message:
        return jsonify({"error": "User ID and message are required"}), 400

    if not update_user_request_count(user_id):
        return jsonify({"error": "API rate limit exceeded"}), 429

    # Generate embedding for the user message
    try:
        user_message_embedding_response = co.embed(texts=[user_message])
        user_message_embedding = user_message_embedding_response.embeddings[0]
    except Exception as e:
        logger.error(f"Cohere API embedding failed: {str(e)}")
        return jsonify({"error": f"Cohere API embedding failed: {str(e)}"}), 500

    # Retrieve all stored documents and embeddings
    documents = get_all_documents_with_embeddings()

    # Calculate similarity between the user message embedding and document embeddings
    relevant_docs = []
    for doc in documents:
        similarity = cosine_similarity(user_message_embedding, doc['embedding'])
        if similarity > 0.1:  # Consider documents with similarity above a certain threshold
            relevant_docs.append({
                "document_id": doc['document_id'],
                "text": doc['text'],
                "similarity": similarity
            })

    # Sort the documents by similarity and take top_k
    relevant_docs = sorted(relevant_docs, key=lambda x: x['similarity'], reverse=True)[:top_k]

    # Combine relevant document texts into context for chat
    context = "\n".join(doc['text'] for doc in relevant_docs)

    # Generate a chat response using Cohere API with context
    try:
        response = co.generate(
            model='command-light',
            prompt=f"Context:\n{context}\n\nUser: {user_message}\nAI:",
            max_tokens=150,
            temperature=0.7
        )
        ai_message = response.generations[0].text.strip()
    except Exception as e:
        logger.error(f"Cohere API chat failed: {str(e)}")
        return jsonify({"error": f"Cohere API chat failed: {str(e)}"}), 500

    return jsonify({"message": ai_message})

# Background task to reset user request counts periodically
def start_background_tasks():
    threading.Thread(target=reset_user_request_counts, daemon=True).start()

# Call this function once when initializing the app to create the table
create_table()
start_background_tasks()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
