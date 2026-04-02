"""
Scraper for Eater NY via RSS feed.
Feed URL: https://ny.eater.com/rss/index.xml
Focuses on restaurant openings, dining news, and celeb-adjacent dining content.
"""

import hashlib
import xml.etree.ElementTree as ET
import re
import requests

RSS_URL = "https://ny.eater.com/rss/index.xml"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Keywords that suggest celebrity/dining relevance
RELEVANCE_KEYWORDS = [
    "spotted", "celeb", "star", "famous", "sighting",
    "dinner", "dining", "restaurant", "brunch", "bar",
    "mayor", "chef", "opening", "hot spot", "hotspot",
]


def strip_html(text):
    return re.sub(r"<[^>]+>", " ", text)


def fetch_posts():
    """Fetch Eater NY articles from RSS."""
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    # Eater uses Atom feed
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(resp.text)
    entries = root.findall(".//atom:entry", ns)

    posts = []
    for entry in entries:
        title = entry.findtext("atom:title", "", ns)
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        url = link_el.get("href", "") if link_el is not None else ""
        summary = strip_html(entry.findtext("atom:summary", "", ns))
        content = strip_html(entry.findtext("atom:content", "", ns))

        body = f"{summary}\n\n{content}".strip()

        # Filter for dining/celebrity relevance
        combined = f"{title} {body}".lower()
        if not any(kw in combined for kw in RELEVANCE_KEYWORDS):
            continue

        post_id = hashlib.md5(url.encode()).hexdigest()
        posts.append({
            "post_id": f"eater-{post_id}",
            "title": title,
            "body": body[:4000],
            "comments": [],
            "source_url": url,
            "subreddit": "Eater NY",
        })

    print(f"  Eater NY RSS: {len(posts)} relevant articles (of {len(entries)} total)")
    return posts
