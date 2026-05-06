#!/usr/bin/env python3
"""Tuesday trivia compile — runs Tue 6pm Sydney, posts to #trivia-report."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import re

import anthropic
import requests

SYDNEY = ZoneInfo("Australia/Sydney")
COMPILE_DAY = 1  # Tuesday
COMPILE_HOUR = 18
DISCORD_MAX_CHARS = 1900
DISCORD_API = "https://discord.com/api/v10"
MODEL = "claude-opus-4-7"


def clean_response_text(text: str) -> str:
    """Tidy up Claude's response for Discord rendering.

    1. Strip any 'Trivia brief — ...' heading (the script prepends its own).
    2. Strip preamble (search narration) before the first section heading.
    3. Ensure each bullet is its own block by inserting blank lines before bullet markers.
    4. Split into paragraph blocks, collapse internal newlines, drop citation residue.
    """
    # Strip any heading emitted by Claude that duplicates the script's header
    text = re.sub(r"\*?\*?(?:Trivia brief|Weekly brief|Tuesday brief)[^\n]*\n?", "", text, flags=re.IGNORECASE)

    # Strip preamble: everything before the first bold all-caps section heading
    # e.g. **AUSTRALIA**, **SPORT**, **SECTION 1**, **NEWS BRIEF**
    match = re.search(r"\*\*(?:SECTION|AUSTRALIA|GLOBAL|SPORT|ENTERTAINMENT|WEIRD|NEWS BRIEF)", text, re.IGNORECASE)
    if match:
        text = text[match.start():]

    # Force each bullet onto its own block by inserting a blank line before bullet markers
    text = re.sub(r"\n(\s*[-*•])", r"\n\n\1", text)

    blocks = re.split(r"\n{2,}", text)
    cleaned = []
    for block in blocks:
        line = re.sub(r"\n+", " ", block).strip()
        if re.fullmatch(r"[\s.,;:\-]+", line):
            continue
        if re.fullmatch(r"\[\^?\d+\]", line):
            continue
        if line:
            cleaned.append(line)
    return "\n\n".join(cleaned).strip()


def in_compile_window(now: datetime) -> bool:
    return now.weekday() == COMPILE_DAY and now.hour == COMPILE_HOUR


def is_first_tuesday_of_month(now: datetime) -> bool:
    # First Tuesday is always within days 1-7
    return now.day <= 7


def fetch_recent_intakes(channel_id: str, bot_token: str, limit: int = 20) -> str:
    headers = {"Authorization": f"Bot {bot_token}"}
    r = requests.get(
        f"{DISCORD_API}/channels/{channel_id}/messages",
        headers=headers,
        params={"limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    messages = list(reversed(r.json()))  # chronological order
    blocks = []
    for m in messages:
        ts = m.get("timestamp", "")[:10]
        content = m.get("content", "").strip()
        if content:
            blocks.append(f"--- {ts} ---\n{content}")
    return "\n\n".join(blocks) if blocks else "(no recent intakes found)"


def load_prompt(date_str: str, intakes: str, include_history: bool) -> str:
    path = Path(__file__).parent / "prompts" / "tuesday_compile.txt"
    text = path.read_text()
    text = text.replace("[DATE]", date_str)
    text = text.replace("[INTAKES]", intakes)
    text = text.replace(
        "[INCLUDE_MONTH_HISTORY]",
        "YES — include the 20 historical events section at the end."
        if include_history
        else "NO — skip the historical events section entirely.",
    )
    return text


def call_claude(prompt: str) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system="You are a trivia research assistant. When you have finished your research, output only the final brief with no preamble, narration, or meta-commentary. Never describe what you are about to do or have done. Begin your response with the first section heading.",
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "\n".join(b.text for b in response.content if hasattr(b, "text"))
    print(f"DEBUG: raw response length={len(raw)}")
    print(f"DEBUG: raw preview (first 300): {raw[:300]!r}")
    return clean_response_text(raw)


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
    if not in_compile_window(now) and not os.environ.get("TRIVIA_FORCE_RUN"):
        print(f"Not the compile window in Sydney ({now:%A %H:%M}); exiting.")
        return

    date_str = now.strftime("%A %d %B %Y")
    include_history = is_first_tuesday_of_month(now)
    print(f"Compiling for {date_str} — month-history: {include_history}")

    intakes = fetch_recent_intakes(
        os.environ["DISCORD_DAILY_CHANNEL_ID"],
        os.environ["DISCORD_BOT_TOKEN_DAILY"],
    )
    prompt = load_prompt(date_str, intakes, include_history)
    compile_text = call_claude(prompt)

    header = f"**Trivia brief — {now:%a %d %b}**\n\n"
    post_to_discord(os.environ["DISCORD_WEBHOOK_WEEKLY"], header + compile_text)
    print("Posted.")


if __name__ == "__main__":
    main()
