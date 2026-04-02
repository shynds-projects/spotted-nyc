"""
Scraper for Page Six celebrity sightings.
Page Six maintains a rolling sightings article at:
  https://pagesix.com/article/celebrity-sightings/
They also have individual articles tagged with "celebrity sightings".
"""

import re
import hashlib
import requests
from bs4 import BeautifulSoup

SIGHTINGS_URL = "https://pagesix.com/article/celebrity-sightings/"
SOCIETY_URL = "https://pagesix.com/tag/celebrity-sightings/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def fetch_sightings_article():
    """Scrape the main rolling sightings article."""
    resp = requests.get(SIGHTINGS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    content = soup.find("div", class_=re.compile("entry-content"))
    if not content:
        return []

    text = content.get_text(separator="\n", strip=True)

    # Split into individual sighting entries (they're separated by dates or line breaks)
    entries = re.split(r"\n(?=\d{1,2}/\d{1,2}\b)", text)

    posts = []
    for entry in entries:
        entry = entry.strip()
        if len(entry) < 30:
            continue
        post_id = hashlib.md5(entry[:200].encode()).hexdigest()
        posts.append({
            "post_id": f"pagesix-sightings-{post_id}",
            "title": "Page Six Celebrity Sightings",
            "body": entry,
            "comments": [],
            "source_url": SIGHTINGS_URL,
            "subreddit": "Page Six",
        })

    return posts


def fetch_society_articles():
    """Scrape Page Six society/sightings column articles."""
    resp = requests.get(SOCIETY_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = soup.find_all("article")
    posts = []

    for article in articles[:15]:
        link_tag = article.find("a", href=True)
        title_tag = article.find(["h2", "h3"])
        if not link_tag:
            continue

        url = link_tag["href"]
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Fetch full article
        try:
            art_resp = requests.get(url, headers=HEADERS, timeout=30)
            art_soup = BeautifulSoup(art_resp.text, "html.parser")
            body_el = art_soup.find("div", class_=re.compile("entry-content"))
            body = body_el.get_text(separator="\n", strip=True) if body_el else ""
        except Exception:
            body = ""

        if not body or len(body) < 50:
            continue

        post_id = hashlib.md5(url.encode()).hexdigest()
        posts.append({
            "post_id": f"pagesix-{post_id}",
            "title": title,
            "body": body[:4000],
            "comments": [],
            "source_url": url,
            "subreddit": "Page Six",
        })

    return posts


def fetch_posts():
    """Fetch all Page Six sighting posts."""
    posts = []
    try:
        posts.extend(fetch_sightings_article())
        print(f"  Page Six sightings article: {len(posts)} entries")
    except Exception as e:
        print(f"  Page Six sightings article failed: {e}")

    try:
        society = fetch_society_articles()
        posts.extend(society)
        print(f"  Page Six tagged articles: {len(society)} articles")
    except Exception as e:
        print(f"  Page Six tagged articles failed: {e}")

    return posts
