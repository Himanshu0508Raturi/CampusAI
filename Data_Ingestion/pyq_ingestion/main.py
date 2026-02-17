import os
import re
import requests
from pymongo import MongoClient
from datetime import datetime, UTC
from dotenv import load_dotenv
load_dotenv()
# -------------------------------
# ENV VARIABLES (SET IN LAMBDA)
# -------------------------------

MONGO_URI = os.environ["MONGO_URI"]
GITHUB_OWNER = os.environ["GITHUB_OWNER"]
GITHUB_REPO = os.environ["GITHUB_REPO"]
GITHUB_BRANCH = os.environ["GITHUB_BRANCH"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

client = MongoClient(MONGO_URI)
db = client["campus_ai"]
collection = db["pyq_papers"]

# -------------------------------
# FETCH REPO TREE
# -------------------------------

def fetch_repo_tree():
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/{GITHUB_BRANCH}?recursive=1"

    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("GitHub API failed")

    return response.json()["tree"]

# -------------------------------
# PARSE PDF METADATA
# -------------------------------

def parse_metadata(file_path):

    # Only allow BTECH CSE
    if not file_path.lower().startswith("btech/cse/"):
        return None

    parts = file_path.split("/")
    file_name = parts[-1]
    lower_path = file_path.lower()

    # Detect semester
    semester_match = re.search(r'sem\s*(\d+)', lower_path)
    if not semester_match:
        return None
    semester = int(semester_match.group(1))

    # Detect subject folder (last folder before file or exam folder)
    subject_name = None

    if parts[-2].lower().startswith(("end", "mid")):
        subject_name = parts[-3]
    else:
        subject_name = parts[-2]

    subject_name = subject_name.replace("-", " ").title()

    # Extract subject code (first alphanumeric block)
    code_match = re.match(r'([a-zA-Z0-9]+)', file_name)
    if not code_match:
        return None
    subject_code = code_match.group(1).upper()

    # Detect exam type
    exam_type = None
    if "end" in file_name.lower():
        exam_type = "end"
    elif "mid" in file_name.lower():
        exam_type = "mid"
    else:
        # fallback if folder contains end/mid
        if "/end/" in lower_path:
            exam_type = "end"
        elif "/mid/" in lower_path:
            exam_type = "mid"
        else:
            return None

    # Extract year
    year_match = re.search(r'(20\d{2})', file_name)
    if not year_match:
        return None
    year = int(year_match.group(1))

    # Extract exam date portion (optional)
    date_match = re.search(r'20\d{2}_(.*?)(?:_set|\.pdf)', file_name.lower())
    exam_date_raw = date_match.group(1) if date_match else None

    # Extract set (optional)
    set_match = re.search(r'set([a-z])', file_name.lower())
    paper_set = set_match.group(1).upper() if set_match else None

    pdf_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{file_path}"

    return {
        "course": "btech",
        "branch": "cse",
        "semester": semester,
        "subject_name": subject_name,
        "subject_code": subject_code,
        "exam_type": exam_type,
        "year": year,
        "exam_date_raw": exam_date_raw,
        "paper_set": paper_set,
        "pdf_url": pdf_url,
        "github_path": file_path,
        "file_name": file_name,
        "is_active": True,
        "source": "github",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

# -------------------------------
# UPSERT (NO DUPLICATES)
# -------------------------------

def upsert_paper(document):
    collection.update_one(
        {"github_path": document["github_path"]},
        {"$set": document},
        upsert=True
    )

# -------------------------------
# MAIN LAMBDA HANDLER
# -------------------------------

def lambda_handler(event, context):

    tree = fetch_repo_tree()

    pdf_files = [
        item["path"]
        for item in tree
        if item["type"] == "blob"
        and item["path"].lower().endswith(".pdf")
        and item["path"].lower().startswith("btech/cse/")
    ]

    processed = 0

    for file_path in pdf_files:
        metadata = parse_metadata(file_path)
        if metadata:
            upsert_paper(metadata)
            processed += 1

    return {
        "statusCode": 200,
        "body": f"BTech CSE ingestion complete. Processed {processed} files."
    }
