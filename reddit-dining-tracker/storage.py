import sqlite3
from datetime import datetime, timezone

DB_PATH = "sightings.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sightings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE NOT NULL,
            celebrity TEXT,
            restaurant TEXT,
            city TEXT,
            date_mentioned TEXT,
            confidence TEXT,
            source_url TEXT,
            scraped_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_sighting(post_id, sighting, source_url):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO sightings
                (post_id, celebrity, restaurant, city, date_mentioned, confidence, source_url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                sighting["celebrity"],
                sighting["restaurant"],
                sighting.get("city"),
                sighting.get("date_mentioned"),
                sighting["confidence"],
                source_url,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return True  # new row inserted
    except sqlite3.IntegrityError:
        return False  # duplicate post_id, skipped
    finally:
        conn.close()


def already_scraped(post_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT 1 FROM sightings WHERE post_id = ?", (post_id,)
    ).fetchone()
    conn.close()
    return row is not None
