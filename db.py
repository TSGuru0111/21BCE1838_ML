import sqlite3
import numpy as np
import pickle

# Connect to SQLite database (or create it if it doesn't exist)
def get_db_connection():
    conn = sqlite3.connect('documents.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to store a document and its embedding in the database
def store_document(text, embedding):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert the embedding (list of floats) to a binary format using pickle
    embedding_blob = pickle.dumps(embedding)

    # Insert the document and embedding into the table
    cursor.execute(
        "INSERT INTO documents (text, embedding) VALUES (?, ?)",
        (text, embedding_blob)
    )
    conn.commit()
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
