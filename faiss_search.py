import faiss
import numpy as np

# Initialize a FAISS index
index = faiss.IndexFlatL2(512)  # Assuming 512-dimensional vectors
documents = ["Document 1", "Document 2", "Document 3"]  # Sample documents
embeddings = np.random.random((3, 512)).astype('float32')  # Fake document embeddings
index.add(embeddings)

def search_documents(query_text, top_k, threshold):
    query_embedding = np.random.random((1, 512)).astype('float32')  # Simulated query embedding
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, dist in zip(indices[0], distances[0]):
        if dist < threshold:
            results.append({"document": documents[i], "score": dist})
    
    return results
