#!/usr/bin/env python3
"""Print recent headlines from Australian news RSS feeds, for the trivia sweep.

Anthropic's WebSearch/WebFetch crawler is blocked from the major AU news domains,
so the daily intake and Tuesday compile can't reach them that way. These feeds are
public RSS and ARE reachable over plain HTTP, so this script pulls them directly
to give Claude Australian material the crawler can't see. Headlines only — open a
specific URL (via WebFetch or curl) to read the full story before quoting detail.

Note: news.com.au is deliberately omitted — it returns HTTP 403 to automated
fetches, including curl.

Usage:
    fetch_au_news.py [per_feed]   # default 12 headlines per feed
"""
import sys
from xml.etree import ElementTree as ET

import requests

UA = {"User-Agent": "Mozilla/5.0 (trivia-bot AU news sweep)"}

FEEDS = [
    ("ABC News (Top Stories)", "https://www.abc.net.au/news/feed/2942460/rss.xml"),
    ("The Guardian Australia", "https://www.theguardian.com/au/rss"),
    ("Sydney Morning Herald", "https://www.smh.com.au/rss/feed.xml"),
    ("The Age", "https://www.theage.com.au/rss/feed.xml"),
    ("7News", "https://7news.com.au/rss"),
    ("9News (National)", "https://www.9news.com.au/national/rss"),
    ("Newcastle Herald", "https://www.newcastleherald.com.au/rss.xml"),
]


def _text(item, tag):
    el = item.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def fetch_feed(url: str, limit: int) -> list[tuple[str, str, str]]:
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    out = []
    for item in root.iter("item"):  # RSS 2.0
        title = _text(item, "title")
        link = _text(item, "link")
        date = _text(item, "pubDate")[:16]  # "Tue, 02 Jun 2026"
        if title:
            out.append((date, title, link))
        if len(out) >= limit:
            break
    return out


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    for name, url in FEEDS:
        print(f"=== {name} ===")
        try:
            items = fetch_feed(url, limit)
        except Exception as e:  # one bad feed shouldn't sink the sweep
            print(f"(could not fetch: {e})\n")
            continue
        for date, title, link in items:
            print(f"- {title}" + (f"  [{date}]" if date else ""))
            if link:
                print(f"    {link}")
        print()


if __name__ == "__main__":
    main()
