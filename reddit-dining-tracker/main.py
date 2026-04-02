import os
import time
from dotenv import load_dotenv
from scraper import get_reddit_client, fetch_posts as fetch_reddit_posts
from scrapers.pagesix import fetch_posts as fetch_pagesix_posts
from scrapers.eater import fetch_posts as fetch_eater_posts
from scrapers.justjared import fetch_posts as fetch_justjared_posts
from scrapers.tmz import fetch_posts as fetch_tmz_posts
from scrapers.deuxmoi import fetch_posts as fetch_deuxmoi_posts
from extractor import extract_sighting
from storage import init_db, save_sighting, already_scraped


def print_summary(new_sightings):
    if not new_sightings:
        print("\nNo new sightings found this run.")
        return

    print(f"\n{'='*70}")
    print(f"  NEW SIGHTINGS ADDED: {len(new_sightings)}")
    print(f"{'='*70}")
    print(f"{'CELEBRITY':<25} {'RESTAURANT':<25} {'CITY':<12} {'SOURCE':<10}")
    print(f"{'-'*70}")
    for s in new_sightings:
        celeb = (s["celebrity"] or "")[:24]
        restaurant = (s["restaurant"] or "")[:24]
        city = (s["city"] or "")[:11]
        source = (s.get("source", "") or "")[:9]
        print(f"{celeb:<25} {restaurant:<25} {city:<12} {source:<10}")
    print(f"{'='*70}\n")


def process_posts(posts, new_sightings):
    """Process a list of posts through the extraction pipeline."""
    skipped_duplicate = 0
    skipped_no_sighting = 0

    for i, post in enumerate(posts, 1):
        print(f"  [{i}/{len(posts)}] {post['title'][:60]}...")

        if already_scraped(post["post_id"]):
            skipped_duplicate += 1
            continue

        result = extract_sighting(post)

        if result is None:
            skipped_no_sighting += 1
            continue

        # Normalize to list (extractor can return a single dict or a list)
        sightings_list = result if isinstance(result, list) else [result]

        for idx, sighting in enumerate(sightings_list):
            pid = f"{post['post_id']}-{idx}" if len(sightings_list) > 1 else post["post_id"]
            inserted = save_sighting(pid, sighting, post["source_url"])
            if inserted:
                sighting["source_url"] = post["source_url"]
                sighting["source"] = post.get("subreddit", "unknown")
                new_sightings.append(sighting)
                print(f"    ✓ Found: {sighting['celebrity']} @ {sighting['restaurant']}")

        # Be polite to the Anthropic API
        time.sleep(0.5)

    return skipped_duplicate, skipped_no_sighting


def run():
    load_dotenv()
    print("Initializing database...")
    init_db()

    new_sightings = []
    total_dupes = 0
    total_skipped = 0

    # --- Reddit (optional — requires API credentials) ---
    if os.getenv("REDDIT_CLIENT_ID"):
        print("\n📡 Reddit")
        try:
            reddit = get_reddit_client()
            reddit_posts = fetch_reddit_posts(reddit)
            d, s = process_posts(reddit_posts, new_sightings)
            total_dupes += d
            total_skipped += s
        except Exception as e:
            print(f"  Reddit failed: {e}")
    else:
        print("\n📡 Reddit — skipped (no REDDIT_CLIENT_ID set)")

    # --- Page Six ---
    print("\n📰 Page Six")
    try:
        pagesix_posts = fetch_pagesix_posts()
        d, s = process_posts(pagesix_posts, new_sightings)
        total_dupes += d
        total_skipped += s
    except Exception as e:
        print(f"  Page Six failed: {e}")

    # --- Eater NY ---
    print("\n🍽️  Eater NY")
    try:
        eater_posts = fetch_eater_posts()
        d, s = process_posts(eater_posts, new_sightings)
        total_dupes += d
        total_skipped += s
    except Exception as e:
        print(f"  Eater NY failed: {e}")

    # --- Just Jared ---
    print("\n⭐ Just Jared")
    try:
        jj_posts = fetch_justjared_posts()
        d, s = process_posts(jj_posts, new_sightings)
        total_dupes += d
        total_skipped += s
    except Exception as e:
        print(f"  Just Jared failed: {e}")

    # --- TMZ ---
    print("\n📺 TMZ")
    try:
        tmz_posts = fetch_tmz_posts()
        d, s = process_posts(tmz_posts, new_sightings)
        total_dupes += d
        total_skipped += s
    except Exception as e:
        print(f"  TMZ failed: {e}")

    # --- DeuxMoi ---
    print("\n💅 DeuxMoi")
    try:
        dm_posts = fetch_deuxmoi_posts()
        d, s = process_posts(dm_posts, new_sightings)
        total_dupes += d
        total_skipped += s
    except Exception as e:
        print(f"  DeuxMoi failed: {e}")

    print(f"\nDone. {total_dupes} duplicates skipped, {total_skipped} posts had no sighting.")
    print_summary(new_sightings)


if __name__ == "__main__":
    run()
