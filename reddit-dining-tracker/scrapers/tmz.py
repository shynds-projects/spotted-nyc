"""
Scraper for TMZ via RSS feed.
Feed URL: https://www.tmz.com/rss.xml
Celebrity news — filter for dining/outing/sighting mentions.
"""

import hashlib
import xml.etree.ElementTree as ET
import re
import requests

RSS_URL = "https://www.tmz.com/rss.xml"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

DINING_KEYWORDS = [
    "restaurant", "dinner", "lunch", "brunch", "dining",
    "spotted", "seen at", "eating", "bar", "cafe", "coffee",
    "night out", "date night", "outing", "club", "party",
    "steakhouse", "sushi", "pizza",
]


def strip_cdata(text):
    text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
    return re.sub(r"<[^>]+>", " ", text).strip()


def fetch_article_body(url):
    """Fetch full article text from a TMZ article URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        # Extract article content
        match = re.search(
            r'<div[^>]*class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>',
            resp.text,
            re.DOTALL,
        )
        if match:
            return re.sub(r"<[^>]+>", " ", match.group(1)).strip()[:4000]

        # Fallback: grab all paragraph text
        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", resp.text, re.DOTALL)
        text = " ".join(re.sub(r"<[^>]+>", "", p).strip() for p in paragraphs)
        return text[:4000]
    except Exception:
        return ""


def fetch_posts():
    """Fetch TMZ articles from RSS, filtered for dining relevance."""
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    items = root.findall(".//item")

    posts = []
    for item in items:
        title = item.findtext("title", "")
        url = item.findtext("link", "")
        description = strip_cdata(item.findtext("description", ""))

        # Quick relevance check on title + description
        combined = f"{title} {description}".lower()
        if not any(kw in combined for kw in DINING_KEYWORDS):
            continue

        # Fetch full article for more context
        body = fetch_article_body(url)
        if not body:
            body = description

        post_id = hashlib.md5(url.encode()).hexdigest()
        posts.append({
            "post_id": f"tmz-{post_id}",
            "title": title,
            "body": body[:4000],
            "comments": [],
            "source_url": url,
            "subreddit": "TMZ",
        })

    print(f"  TMZ RSS: {len(posts)} relevant articles (of {len(items)} total)")
    return posts
