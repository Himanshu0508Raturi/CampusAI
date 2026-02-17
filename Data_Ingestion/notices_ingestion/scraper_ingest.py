import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

from db import post_exists, hash_exists, vector_col
from embedder import generate_embeddings_batch
from chunker import chunk_text

BASE_URL = "http://btechcsegehu.in/notices-2/"

def scrape_and_ingest():

    print("Starting Scraper...")

    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")

    new_count = 0

    for article in articles:

        raw_id = article.get("id")
        if not raw_id:
            continue

        post_id = raw_id.replace("post-", "")

        # Stop early
        if post_exists(post_id):
            print("Reached old post. Stopping crawl.")
            break

        # ---- Extract Title & Notice URL ----
        title_tag = article.find("h1", class_="entry-title")
        notice_url = title_tag.find("a")["href"]
        title = title_tag.text.strip()

        # ---- Extract Date ----
        date = article.find("time")["datetime"]

        # ---- Extract Content ----
        content_div = article.find("div", class_="entry-content")
        content = content_div.get_text(separator=" ", strip=True)

        # ---- Extract PDF ----
        pdf_url = None
        pdf_link_tag = content_div.find("a", href=True)
        if pdf_link_tag and ".pdf" in pdf_link_tag["href"].lower():
            pdf_url = pdf_link_tag["href"]

        # ---- Hash ----
        hash_input = title + date + content
        content_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        if hash_exists(content_hash):
            print(f"Duplicate content detected: {title}")
            continue

        print(f"New Notice Found: {title}")

        # ---- Chunk + Embed ----
        chunks = chunk_text(content)
        embeddings = generate_embeddings_batch(chunks)

        documents = []

        for chunk, embedding in zip(chunks, embeddings):
            documents.append({
                "post_id": post_id,
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "title": title,
                    "date": date,
                    "notice_url": notice_url,
                    "pdf_url": pdf_url,
                    "department": "CSE",
                    "type": "notice",
                    "content_hash": content_hash,
                    "created_at": datetime.utcnow()
                }
            })

        if documents:
            vector_col.insert_many(documents)

        new_count += 1

    print(f"Total New Notices Processed: {new_count}")
