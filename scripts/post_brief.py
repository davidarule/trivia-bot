#!/usr/bin/env python3
"""Post a Claude-generated trivia brief to Discord.

Usage:
    post_brief.py daily  [brief_file]   # -> #daily-trivia
    post_brief.py weekly [brief_file]   # -> #trivia-report

Reads the brief from brief_file if given, otherwise from stdin. Claude Code does
the web research and writes the brief (following scripts/prompts/*.txt); this
script just prepends the dated header, chunks the text under Discord's message
limit, and posts it via the channel webhook in .env.
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

SYDNEY = ZoneInfo("Australia/Sydney")
DISCORD_MAX_CHARS = 1900  # headroom under Discord's 2000 limit

TARGETS = {
    "daily": ("DISCORD_WEBHOOK_DAILY", "Daily intake"),
    "weekly": ("DISCORD_WEBHOOK_WEEKLY", "Trivia brief"),
}


def load_env(path: Path) -> None:
    """Populate os.environ from .env, without overriding already-set vars."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


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


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in TARGETS:
        sys.exit("usage: post_brief.py {daily|weekly} [brief_file]")
    env_key, label = TARGETS[sys.argv[1]]

    load_env(Path(__file__).resolve().parent.parent / ".env")
    webhook = os.environ.get(env_key)
    if not webhook:
        sys.exit(f"{env_key} not set (check .env)")

    brief = (Path(sys.argv[2]).read_text() if len(sys.argv) > 2 else sys.stdin.read()).strip()
    if not brief:
        sys.exit("no brief content provided (file or stdin was empty)")

    now = datetime.now(SYDNEY)
    header = f"**{label} — {now:%a %d %b}**\n\n"
    chunks = split_for_discord(header + brief)
    for i, chunk in enumerate(chunks, 1):
        r = requests.post(webhook, json={"content": chunk}, timeout=30)
        r.raise_for_status()
        print(f"chunk {i}/{len(chunks)} -> HTTP {r.status_code}")
    print("Posted.")


if __name__ == "__main__":
    main()
