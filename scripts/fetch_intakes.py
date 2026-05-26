#!/usr/bin/env python3
"""Print the week's #daily-trivia intakes to stdout, for the Tuesday compile.

Claude Code reads this output as the week's daily intakes, then does a fresh web
sweep and compiles the Tuesday brief (see scripts/prompts/tuesday_compile.txt)
before posting with post_brief.py. Requires the daily bot token + channel id in
.env.

Usage:
    fetch_intakes.py [limit]   # default limit 20
"""
import os
import sys
from pathlib import Path

import requests

DISCORD_API = "https://discord.com/api/v10"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


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


def main() -> None:
    load_env(Path(__file__).resolve().parent.parent / ".env")
    channel = os.environ.get("DISCORD_DAILY_CHANNEL_ID")
    token = os.environ.get("DISCORD_BOT_TOKEN_DAILY")
    if not channel or not token:
        sys.exit("DISCORD_DAILY_CHANNEL_ID / DISCORD_BOT_TOKEN_DAILY not set (check .env)")
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print(fetch_recent_intakes(channel, token, limit))


if __name__ == "__main__":
    main()
