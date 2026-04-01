import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

START_URL = "https://gehu.ac.in/"
DOMAIN = urlparse(START_URL).netloc
OUTPUT_FILE = "gehu-top-placement.txt"
MAX_PAGES = 300
CRAWL_DELAY = 0.7      # seconds

headers = {
    "User-Agent": "Mozilla/5.0 (DeepCrawler/2.0)"
}

visited = set()
queue = deque([START_URL])

def is_valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if parsed.netloc != DOMAIN:
        return False
    if any(x in url.lower() for x in ["logout", "login", "signup", "mailto", "javascript"]):
        return False
    return True

def clean_text(text):
    return " ".join(text.split())

# clear output file
open(OUTPUT_FILE, "w", encoding="utf-8").close()

while queue and len(visited) < MAX_PAGES:
    url = queue.popleft()
    if url in visited:
        continue

    print(f"[SCRAPING] {url}")
    visited.add(url)

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            continue
    except requests.RequestException:
        continue

    soup = BeautifulSoup(res.text, "html.parser")

    # remove noisy sections
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else "No Title"

    extracted_text = []

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "td"]):
        text = clean_text(tag.get_text())
        if len(text) > 50:
            extracted_text.append(text)

    # write content
    if extracted_text:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 90 + "\n")
            f.write(f"URL: {url}\n")
            f.write(f"TITLE: {title}\n\n")
            for line in extracted_text:
                f.write(f"- {line}\n")

    # extract and enqueue deeper links
    for a in soup.find_all("a", href=True):
        next_url = urljoin(url, a["href"].strip())
        next_url = next_url.split("#")[0]  # remove fragments

        if is_valid_url(next_url) and next_url not in visited:
            queue.append(next_url)

    time.sleep(CRAWL_DELAY)

print("Deep crawling completed")
