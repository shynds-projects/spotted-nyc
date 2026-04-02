import os
import json
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data extraction assistant. Your job is to read articles, posts, and comments
about celebrities and extract structured dining/venue information.

Look for ANY mention of a celebrity at a specific restaurant, bar, club, cafe, hotel dining room,
or other food/drink venue. This includes:
- Direct sighting reports ("X was spotted at Y")
- Event coverage ("X celebrated at Y", "X hosted dinner at Y")
- Casual mentions ("X loves eating at Y", "X was seen having brunch at Y")
- Articles about where celebrities dine

Return a JSON object in exactly this shape if a relevant celebrity + venue connection is found:
{
  "celebrity": "full name of the celebrity",
  "restaurant": "name of the restaurant, bar, or venue",
  "city": "city name or null",
  "date_mentioned": "any date reference mentioned (e.g. 'last Tuesday', 'March 5') or null",
  "confidence": "high | medium | low"
}

If the text contains MULTIPLE celebrity+venue pairs, return an array of JSON objects.

Return null (not a JSON object) if:
- No specific celebrity is mentioned
- No specific restaurant, bar, or dining venue is mentioned
- The content is not about a real dining/venue visit

Confidence levels:
- high: clear celebrity name + clear venue name + specific details
- medium: celebrity or venue is implied/uncertain, or details are vague
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

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = raw.strip()

    if raw.lower() == "null" or not raw:
        return None

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return None

    # Handle both single objects and arrays
    if isinstance(result, list):
        valid = []
        for item in result:
            if not isinstance(item, dict):
                continue
            if item.get("confidence") == "low":
                continue
            if not item.get("celebrity") or not item.get("restaurant"):
                continue
            valid.append(item)
        return valid if valid else None

    if not isinstance(result, dict):
        return None

    if result.get("confidence") == "low":
        return None
    if not result.get("celebrity") or not result.get("restaurant"):
        return None

    return result
