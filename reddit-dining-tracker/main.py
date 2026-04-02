import time
from scraper import get_reddit_client, fetch_posts
from extractor import extract_sighting
from storage import init_db, save_sighting, already_scraped


def print_summary(new_sightings):
    if not new_sightings:
        print("\nNo new sightings found this run.")
        return

    print(f"\n{'='*70}")
    print(f"  NEW SIGHTINGS ADDED: {len(new_sightings)}")
    print(f"{'='*70}")
    print(f"{'CELEBRITY':<25} {'RESTAURANT':<25} {'CITY':<12} {'CONF':<8}")
    print(f"{'-'*70}")
    for s in new_sightings:
        celeb = (s["celebrity"] or "")[:24]
        restaurant = (s["restaurant"] or "")[:24]
        city = (s["city"] or "")[:11]
        conf = s["confidence"] or ""
        print(f"{celeb:<25} {restaurant:<25} {city:<12} {conf:<8}")
    print(f"{'='*70}\n")


def run():
    print("Initializing database...")
    init_db()

    print("Connecting to Reddit...")
    reddit = get_reddit_client()

    print("Fetching posts...")
    posts = fetch_posts(reddit)

    new_sightings = []
    skipped_duplicate = 0
    skipped_no_sighting = 0

    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] Processing: {post['title'][:60]}...")

        if already_scraped(post["post_id"]):
            skipped_duplicate += 1
            continue

        sighting = extract_sighting(post)

        if sighting is None:
            skipped_no_sighting += 1
            continue

        inserted = save_sighting(post["post_id"], sighting, post["source_url"])
        if inserted:
            sighting["source_url"] = post["source_url"]
            new_sightings.append(sighting)
            print(f"  ✓ Found: {sighting['celebrity']} @ {sighting['restaurant']}")

        # Be polite to the Anthropic API
        time.sleep(0.5)

    print(f"\nDone. {skipped_duplicate} duplicates skipped, {skipped_no_sighting} posts had no sighting.")
    print_summary(new_sightings)


if __name__ == "__main__":
    run()
