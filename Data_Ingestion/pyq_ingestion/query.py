import re
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]

client = MongoClient(MONGO_URI)
db = client["campus_ai"]
collection = db["pyq_papers"]


def parse_user_query(text):

    text = text.lower()

    query = {
        "course": "btech",
        "branch": "cse",
        "is_active": True
    }

    # ----------------------------
    # Extract semester
    # ----------------------------
    sem_match = re.search(r'sem\s*(\d+)', text)
    if sem_match:
        query["semester"] = int(sem_match.group(1))
    else:
        num_match = re.search(r'\b([3-8])\b', text)
        if num_match:
            query["semester"] = int(num_match.group(1))

    # ----------------------------
    # Extract exam type
    # ----------------------------
    if "end" in text:
        query["exam_type"] = "end"
    elif "mid" in text:
        query["exam_type"] = "mid"

    # ----------------------------
    # Extract subject code
    # ----------------------------
    code_match = re.search(r'[a-z]{3,4}\d{3}', text)
    if code_match:
        query["subject_code"] = code_match.group(0).upper()
    else:
        # Remove common words
        cleaned = re.sub(r'\b(btech|cse|sem|semester|end|mid|paper|papers|\d)\b', '', text)
        cleaned = cleaned.strip()

        if cleaned:
            query["subject_name"] = {
                "$regex": cleaned,
                "$options": "i"
            }

    return query


def search_papers(user_query):

    mongo_query = parse_user_query(user_query)

    print("Mongo Query:", mongo_query)

    results = collection.find(mongo_query).sort("year", -1)

    papers = []

    for doc in results:
        papers.append({
            "subject_name": doc["subject_name"],
            "subject_code": doc["subject_code"],
            "semester": doc["semester"],
            "exam_type": doc["exam_type"],
            "year": doc["year"],
            "paper_set": doc.get("paper_set"),
            "pdf_url": doc["pdf_url"]
        })

    return papers


# ----------------------------
# Run locally
# ----------------------------

if __name__ == "__main__":
    query = "btech cse 6 sem full stack web development end paper"

    results = search_papers(query)

    for r in results:
        print(r["year"], r["pdf_url"])
