"""
Scraper for DeuxMoi via Substack RSS + public web content.
Feed URL: https://deuxmoi.substack.com/feed
Also scrapes deuxmoi.world for any public sighting content.

Note: DeuxMoi's Substack Cheat Sheets are paywalled, but titles
and public snippets still contain useful sighting info.
"""

import hashlib
import xml.etree.ElementTree as ET
import re
import requests
from bs4 import BeautifulSoup

SUBSTACK_RSS = "https://deuxmoi.substack.com/feed"
DEUXMOI_WORLD = "https://www.deuxmoi.world/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

DINING_KEYWORDS = [
    "restaurant", "dinner", "lunch", "brunch", "dining",
    "spotted", "seen", "eating", "bar", "cafe", "coffee",
    "night out", "date night", "outing", "club",
    "sighting", "celebrity", "celeb",
]


def strip_html(text):
    return re.sub(r"<[^>]+>", " ", text).strip()


def fetch_substack_posts():
    """Fetch DeuxMoi Substack RSS — cheat sheets and public posts."""
    resp = requests.get(SUBSTACK_RSS, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    items = root.findall(".//item")

    posts = []
    for item in items:
        title = item.findtext("title", "")
        url = item.findtext("link", "")
        description = item.findtext("description", "")
        content_el = item.find(
            "{http://purl.org/rss/1.0/modules/content/}encoded"
        )
        content = strip_html(content_el.text) if content_el is not None and content_el.text else ""

        # Only process Cheat Sheet posts (the ones with actual sighting content)
        if "cheat sheet" not in title.lower():
            continue

        # Try fetching the full page for any public content
        body = description
        try:
            page_resp = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(page_resp.text, "html.parser")
            # Substack renders some content publicly before the paywall
            body_div = soup.find("div", class_=re.compile("body"))
            if body_div:
                public_text = body_div.get_text(separator="\n", strip=True)
                if len(public_text) > len(body):
                    body = public_text
        except Exception:
            pass

        if len(body) < 30:
            continue

        post_id = hashlib.md5(url.encode()).hexdigest()
        posts.append({
            "post_id": f"deuxmoi-{post_id}",
            "title": title,
            "body": body[:4000],
            "comments": [],
            "source_url": url,
            "subreddit": "DeuxMoi",
        })

    return posts


def fetch_deuxmoi_world():
    """Scrape deuxmoi.world for any public sighting content."""
    try:
        resp = requests.get(DEUXMOI_WORLD, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article")

        posts = []
        for article in articles[:10]:
            link = article.find("a", href=True)
            title_el = article.find(["h2", "h3"])
            if not link:
                continue

            url = link["href"]
            if not url.startswith("http"):
                url = f"https://www.deuxmoi.world{url}"

            title = title_el.get_text(strip=True) if title_el else ""
            text = article.get_text(separator=" ", strip=True)

            combined = f"{title} {text}".lower()
            if not any(kw in combined for kw in DINING_KEYWORDS):
                continue

            post_id = hashlib.md5(url.encode()).hexdigest()
            posts.append({
                "post_id": f"deuxmoi-world-{post_id}",
                "title": title,
                "body": text[:4000],
                "comments": [],
                "source_url": url,
                "subreddit": "DeuxMoi",
            })

        return posts
    except Exception:
        return []


def fetch_posts():
    """Fetch all DeuxMoi content."""
    posts = []

    substack = fetch_substack_posts()
    posts.extend(substack)
    print(f"  DeuxMoi Substack: {len(substack)} cheat sheets")

    world = fetch_deuxmoi_world()
    posts.extend(world)
    print(f"  DeuxMoi World: {len(world)} articles")

    return posts
