"""
Scraper for Just Jared via RSS feed.
Feed URL: https://www.justjared.com/feed/
Celebrity news with frequent dining/outing mentions.
"""

import hashlib
import xml.etree.ElementTree as ET
import re
import requests

RSS_URL = "https://www.justjared.com/feed/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

DINING_KEYWORDS = [
    "restaurant", "dinner", "lunch", "brunch", "dining",
    "spotted", "seen at", "eating", "bar", "cafe", "coffee",
    "night out", "date night", "outing",
]


def strip_html(text):
    return re.sub(r"<[^>]+>", " ", text)


def fetch_posts():
    """Fetch Just Jared articles from RSS."""
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    items = root.findall(".//item")

    posts = []
    for item in items:
        title = item.findtext("title", "")
        url = item.findtext("link", "")
        description = strip_html(item.findtext("description", ""))
        content_el = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
        content = strip_html(content_el.text) if content_el is not None and content_el.text else ""

        body = f"{description}\n\n{content}".strip()

        # Filter for dining relevance
        combined = f"{title} {body}".lower()
        if not any(kw in combined for kw in DINING_KEYWORDS):
            continue

        post_id = hashlib.md5(url.encode()).hexdigest()
        posts.append({
            "post_id": f"justjared-{post_id}",
            "title": title,
            "body": body[:4000],
            "comments": [],
            "source_url": url,
            "subreddit": "Just Jared",
        })

    print(f"  Just Jared RSS: {len(posts)} relevant articles (of {len(items)} total)")
    return posts
