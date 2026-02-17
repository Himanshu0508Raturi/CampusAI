import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-embedding-001"

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def generate_embeddings_batch(text_chunks):
    """
    Generate embeddings using Google Gemini embedding model.
    """

    if not text_chunks:
        return []

    endpoint = f"{BASE_URL}/{MODEL_NAME}:embedContent?key={GEMINI_API_KEY}"

    embeddings = []

    for text in text_chunks:
        response = requests.post(
            endpoint,
            json={
                "content": {
                    "parts": [
                        {"text": text}
                    ]
                }
            }
        )

        if response.status_code != 200:
            raise Exception(f"Gemini API Error: {response.text}")

        body = response.json()
        embeddings.append(body["embedding"]["values"])

    return embeddings
