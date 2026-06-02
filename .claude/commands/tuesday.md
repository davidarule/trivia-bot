Fire the Tuesday trivia compile. YOU (Claude) compile the brief from the week's
intakes plus a fresh web sweep, then post it — the scripts no longer call the
Anthropic API.

Workflow:
1. Fetch the week's daily intakes — pick the interpreter the way the wrappers do
   (`.venv` if present, else system `python3`):
       PY=$([ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
       "$PY" scripts/fetch_intakes.py
   It prints the #daily-trivia messages from the past week — the primary input.
2. Read LAST WEEK'S Tuesday brief so you can drop anything it already covered.
   It lives in #trivia-report (channel id `1501358120725909504`). Read it with
   the daily bot token, sourcing `.env` in the shell — NEVER print the token:
       set -a; source .env; set +a
       curl -s -H "Authorization: Bot $DISCORD_BOT_TOKEN_DAILY" \
         "https://discord.com/api/v10/channels/1501358120725909504/messages?limit=30"
3. Read the spec at `scripts/prompts/tuesday_compile.txt` and follow it exactly.
   Substitute today's date for [DATE] and the fetched intakes for [INTAKES]. Do a
   fresh web sweep, and generate Section 4 (on this day) and Section 6
   (Quizmasters Fans & Followers, from the raw HTML at quizmasters.com.au) fresh.
   The sweep is the MAIN source of fresh material (intakes are often days old), so:
   - Run BOTH anchor searches (verify known events) AND broad discovery searches
     ("weird/viral/record/science/business this week") — the fun/quirky half only
     surfaces from discovery. Don't skip it.
   - Recency-check every current story: confirm it broke in the last ~7-10 days
     (original date, not a syndicated re-post). No stale items, no
     "announcement of a future announcement".
   - Make the Global section a DIVERSE mix (politics, business, science/space,
     royals, culture) and don't repeat last week's global beat. It's the section
     most likely to come out thin — push it to 4-6 strong bullets.
   - The big AU news sites aren't crawlable; reach AU content via Wikipedia
     "2026 in Australia", AAP, and non-blocked outlets.
4. Apply the compilation rules: drop stories already in last week's brief, dedup
   across intakes, drop stale stories, promote ones that have grown, and enforce
   the clean-named-answer hard filter.
5. Write the compiled brief to a temp file (e.g. `/tmp/tuesday-brief.md`),
   beginning directly with the first section heading — no preamble.
6. Show the user the full compiled brief and get their sign-off BEFORE posting.
   Note honestly anything weak (thin section, AU/global balance off, light week).
   Post only after they approve.
7. Post it: `./tuesday.sh /tmp/tuesday-brief.md` — the wrapper loads `.env` and
   posts to #trivia-report via the webhook.
8. Check stdout for the "Posted." confirmation line. If it appeared, tell the
   user it posted and to verify in #trivia-report. If the script failed or
   printed anything unexpected, surface the actual output and stop — do NOT
   claim success.

Don't narrate each search as you go. Sweep thoroughly, compile, show the draft,
post on approval, and report.
