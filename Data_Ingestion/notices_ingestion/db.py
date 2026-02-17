from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["campus_ai"]

vector_col = db["notice_vector"] 


def post_exists(post_id):
    return vector_col.find_one({"post_id": post_id}) is not None


def hash_exists(hash_value):
    return vector_col.find_one({"metadata.content_hash": hash_value}) is not None
