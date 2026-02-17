from db import vector_col
from embedder import generate_embeddings_batch

INDEX_NAME = "default"

def retrieve_notices(query, limit=5):

    # Embed user query
    query_embedding = generate_embeddings_batch([query])[0]

    pipeline = [
        {
            "$vectorSearch": {
                "index": INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "post_id": 1,
                "content": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(vector_col.aggregate(pipeline))
    return results
