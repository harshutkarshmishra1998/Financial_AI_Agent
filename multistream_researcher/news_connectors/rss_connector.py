
import feedparser

def fetch_rss(url):
    feed = feedparser.parse(url)
    docs = []
    for e in feed.entries:
        docs.append({
            "title": e.get("title"),
            "content": e.get("summary"),
            "url": e.get("link"),
            "date": e.get("published")
        })
    return docs
