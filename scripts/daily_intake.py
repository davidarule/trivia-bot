#!/usr/bin/env python3
"""Daily trivia intake — runs Mon/Wed/Fri 5pm Sydney time, posts to #daily-trivia."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic
import requests

SYDNEY = ZoneInfo("Australia/Sydney")
INTAKE_DAYS = {0, 2, 4}  # Mon, Wed, Fri
INTAKE_HOUR = 17
DISCORD_MAX_CHARS = 1900  # headroom under Discord's 2000 limit
MODEL = "claude-opus-4-7"


def in_intake_window(now: datetime) -> bool:
    return now.weekday() in INTAKE_DAYS and now.hour == INTAKE_HOUR


def load_prompt(date_str: str) -> str:
    path = Path(__file__).parent / "prompts" / "daily_intake.txt"
    return path.read_text().replace("[DATE]", date_str)


def call_claude(prompt: str) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(b.text for b in response.content if hasattr(b, "text"))


def split_for_discord(text: str, limit: int = DISCORD_MAX_CHARS) -> list[str]:
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split = text.rfind("\n", 0, limit)
        if split <= 0:
            split = limit
        chunks.append(text[:split])
        text = text[split:].lstrip()
    return chunks


def post_to_discord(webhook_url: str, content: str) -> None:
    for chunk in split_for_discord(content):
        r = requests.post(webhook_url, json={"content": chunk}, timeout=30)
        r.raise_for_status()


def main() -> None:
    now = datetime.now(SYDNEY)
    if not in_intake_window(now):
        print(f"Not an intake window in Sydney ({now:%A %H:%M}); exiting.")
        return

    date_str = now.strftime("%A %d %B %Y")
    print(f"Generating daily intake for {date_str}")
    prompt = load_prompt(date_str)
    intake_text = call_claude(prompt)

    header = f"**Daily intake — {now:%a %d %b}**\n\n"
    post_to_discord(os.environ["DISCORD_WEBHOOK_DAILY"], header + intake_text)
    print("Posted.")


if __name__ == "__main__":
    main()
