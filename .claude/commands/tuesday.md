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
   fresh web sweep for anything that broke since the most recent intake, and
   generate Section 4 (on this day) and Section 6 (Quizmasters Fans & Followers,
   from the raw HTML at quizmasters.com.au) fresh.
4. Apply the compilation rules: drop stories already in last week's brief, dedup
   across intakes, drop stale stories, promote ones that have grown, and enforce
   the clean-named-answer hard filter.
5. Write the compiled brief to a temp file (e.g. `/tmp/tuesday-brief.md`),
   beginning directly with the first section heading — no preamble.
6. Post it: `./tuesday.sh /tmp/tuesday-brief.md` — the wrapper loads `.env` and
   posts to #trivia-report via the webhook.
7. Check stdout for the "Posted." confirmation line. If it appeared, tell the
   user it posted and to verify in #trivia-report. If the script failed or
   printed anything unexpected, surface the actual output and stop — do NOT
   claim success.

Be brief. Don't narrate the research. Compile, post, and report.
