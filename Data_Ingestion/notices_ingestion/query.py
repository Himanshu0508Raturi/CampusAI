from retriever import retrieve_notices

results = retrieve_notices("What is pbl notice for 1st phase evaluation", limit=3)

for r in results:
    print("Title:", r["metadata"]["title"])
    print("Date:", r["metadata"]["date"])
    print("Notice URL:", r["metadata"]["notice_url"])
    print("Score:", r["score"])
    print("Content:",r["content"])
    print("-" * 50)
