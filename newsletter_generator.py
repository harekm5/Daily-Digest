"""
Daily Newsletter Generator
Fetches curated stories via Claude API + web search and emails them via Gmail SMTP.
"""

import os
import json
import smtplib
import re
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from zoneinfo import ZoneInfo
from anthropic import Anthropic
from prompts import (
    CATEGORY_PROMPTS,
    SECTION_META,
    EMAIL_TEMPLATE_HEADER,
    EMAIL_TEMPLATE_FOOTER,
)

# --- Config from environment ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", GMAIL_USER)

MODEL = "claude-sonnet-4-6"
TIMEZONE = ZoneInfo("America/Los_Angeles")

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def should_run_now() -> bool:
    """Run if it's the morning send window in Pacific time.

    GitHub Actions cron is best-effort and can be delayed 15-60+ minutes.
    We schedule both 13:00 and 14:00 UTC; whichever lands in the 5-7 AM PT
    window wins. Only one of the two will fall in that window during any
    given DST regime, so we still only send once per day.
    """
    if os.environ.get("FORCE_RUN") == "1":
        return True
    pt_hour = datetime.now(TIMEZONE).hour
    return 5 <= pt_hour <= 7


def fetch_category(category_key: str, prompt_config: dict) -> dict:
    """Run a single Claude API call with web search for one category."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=prompt_config["system"],
        messages=[{"role": "user", "content": prompt_config["user"]}],
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 6,
            }
        ],
    )

    # Extract text from non-tool blocks
    final_text = "".join(b.text for b in response.content if b.type == "text")

    # Strip optional code fences and locate the JSON object
    cleaned = re.sub(r"```(?:json)?", "", final_text).replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON found in response for {category_key}:\n{final_text[:500]}")

    parsed = json.loads(cleaned[start : end + 1])
    if "stories" not in parsed or not isinstance(parsed["stories"], list):
        raise ValueError(f"Malformed response for {category_key}: missing 'stories' list")
    return parsed


def render_story(story: dict) -> str:
    title = story.get("title", "Untitled")
    summary = story.get("summary", "")
    why = story.get("why_it_matters", "")
    url = story.get("url", "#")
    return f"""
    <div class="story">
      <h3 class="headline"><a href="{url}">{title}</a></h3>
      <p class="summary">{summary}</p>
      <p class="why"><strong>Why it matters:</strong> {why}</p>
    </div>
    """


def render_section(title: str, emoji: str, intro: str, stories: list) -> str:
    if not stories:
        body = '<p class="empty">No stories returned for this category today.</p>'
    else:
        body = "".join(render_story(s) for s in stories)
    return f"""
    <section class="category">
      <h2>{emoji} {title}</h2>
      <p class="intro">{intro}</p>
      {body}
    </section>
    """


def build_html(category_results: dict) -> str:
    today = datetime.now(TIMEZONE).strftime("%A, %B %d, %Y")
    sections = ""
    for key, title, emoji, intro in SECTION_META:
        result = category_results.get(key, {})
        sections += render_section(title, emoji, intro, result.get("stories", []))
    return EMAIL_TEMPLATE_HEADER.format(date=today) + sections + EMAIL_TEMPLATE_FOOTER


def send_email(html: str, subject: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)


def main() -> int:
    if not should_run_now():
        print(f"Skipping: current PT hour is {datetime.now(TIMEZONE).hour}, not 6.")
        return 0

    print("Generating daily newsletter...")
    results = {}
    for key, config in CATEGORY_PROMPTS.items():
        print(f"  -> Fetching '{key}'")
        try:
            results[key] = fetch_category(key, config)
            print(f"     {len(results[key].get('stories', []))} stories")
        except Exception as e:
            print(f"     ERROR: {e}")
            results[key] = {"stories": []}

    html = build_html(results)
    today_short = datetime.now(TIMEZONE).strftime("%b %d")
    send_email(html, f"Daily Brief — {today_short}")
    print(f"Sent to {RECIPIENT_EMAIL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
    
