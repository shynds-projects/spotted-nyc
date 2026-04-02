import os
import praw
from dotenv import load_dotenv

load_dotenv()

SUBREDDITS = [
    "Deuxmoi",
    "NYCinfluencersnark",
    "LAsnark",
    "popculturechat",
    "BravoRealHousewives",
    "KUWTK",
    "celebsgossip",
    "NYCFood",
    "FoodNYC",
    "PopCulture",
    "entertainmentgossip",
]
SEARCH_QUERY = "restaurant OR dinner OR spotted OR eating OR lunch OR brunch OR bar OR cafe"
POST_LIMIT = 100


def get_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )


def fetch_posts(reddit):
    posts = []
    for sub_name in SUBREDDITS:
        subreddit = reddit.subreddit(sub_name)
        results = subreddit.search(
            SEARCH_QUERY,
            sort="new",
            time_filter="week",
            limit=POST_LIMIT,
        )
        for post in results:
            comments = []
            post.comments.replace_more(limit=0)
            for comment in post.comments:
                if comment.body and len(comment.body.strip()) > 10:
                    comments.append(comment.body.strip())

            posts.append({
                "post_id": post.id,
                "title": post.title,
                "body": post.selftext.strip(),
                "comments": comments[:20],  # top 20 comments
                "source_url": f"https://reddit.com{post.permalink}",
                "subreddit": sub_name,
            })

    print(f"Fetched {len(posts)} posts across {len(SUBREDDITS)} subreddits.")
    return posts
