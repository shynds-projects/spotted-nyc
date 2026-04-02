import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data extraction assistant. Your job is to read Reddit posts and comments
about celebrity sightings and extract structured dining information.

Return a JSON object in exactly this shape if a relevant celebrity dining sighting is found:
{
  "celebrity": "full name of the celebrity or null",
  "restaurant": "name of the restaurant or bar or null",
  "city": "city name or null",
  "date_mentioned": "any date reference mentioned (e.g. 'last Tuesday', 'March 5') or null",
  "confidence": "high | medium | low"
}

Return null (not a JSON object) if:
- No specific celebrity is mentioned
- No specific restaurant, bar, or dining venue is mentioned
- The post is not about a real dining sighting (e.g. it's a meme, opinion, or unrelated gossip)

Confidence levels:
- high: clear celebrity name + clear restaurant name + specific details
- medium: celebrity or restaurant is implied/uncertain, or details are vague
- low: very speculative or secondhand

Return only raw JSON with no markdown, no explanation."""


def extract_sighting(post):
    content = f"Title: {post['title']}\n"
    if post["body"]:
        content += f"Post: {post['body']}\n"
    if post["comments"]:
        content += "Comments:\n" + "\n".join(f"- {c}" for c in post["comments"])

    # Trim to avoid token limits
    content = content[:4000]

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": content}],
        system=SYSTEM_PROMPT,
    )

    raw = message.content[0].text.strip()

    if raw.lower() == "null" or not raw:
        return None

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if not isinstance(result, dict):
        return None

    # Filter out low confidence and incomplete results
    if result.get("confidence") == "low":
        return None
    if not result.get("celebrity") or not result.get("restaurant"):
        return None

    return result
