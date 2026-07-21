Fire the Tuesday trivia compile. YOU (Claude) compile the brief from the week's
intakes plus a fresh web sweep, then post it — the scripts no longer call the
Anthropic API.

Workflow:
1. Fetch the week's daily intakes:
       python3 scripts/fetch_intakes.py
   (Use `.venv/bin/python` instead if the venv exists — both are allowlisted for
   unattended runs; the plain-`python3` form is the default because the timer
   runs headless and every command must match the settings.json allowlist.)
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
   - The big AU news sites aren't crawlable; run `scripts/fetch_au_news.py` for
     AU headlines via RSS (ABC, Guardian AU, SMH, The Age, 7News, 9News,
     Newcastle Herald), plus Wikipedia "2026 in Australia". Open a specific story
     to confirm detail before quoting it.
4. Apply the compilation rules: drop stories already in last week's brief, dedup
   across intakes, drop stale stories, promote ones that have grown, and enforce
   the clean-named-answer hard filter.
5. Write the compiled brief to a temp file (e.g. `/tmp/tuesday-brief.md`),
   beginning directly with the first section heading — no preamble.
6. Post it directly: `./tuesday.sh /tmp/tuesday-brief.md` — the wrapper loads
   `.env` and posts to #trivia-report via the webhook. There is NO approval
   gate: David removed it on 2026-07-21 ("its working well") so the compile can
   fire unattended from the trivia-tuesday systemd timer. If a human is present
   and asks to review first, showing the draft is still fine — but never block
   an unattended run waiting for input.
7. Check stdout for the "Posted." confirmation line. If it appeared, report
   success. If the script failed or printed anything unexpected, surface the
   actual output and stop — do NOT claim success.
8. End with a short honest quality note in your final output (NOT in the brief
   itself — it must not reach Discord): thin sections, AU/global balance off,
   stale intakes, a light week. On timer runs this lands in
   ~/.local/state/trivia-bot/tuesday.log where David can review it.

Don't narrate each search as you go. Sweep thoroughly, compile, post, and
report.
