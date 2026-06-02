Fire the daily trivia intake. YOU (Claude) do the research and write the brief,
then post it — the scripts no longer call the Anthropic API.

Workflow:
1. Read the spec at `scripts/prompts/daily_intake.txt` and follow it exactly:
   coverage, story types, the hard "clean named/numbered answer" filter, the
   exclude list, the five section headings, and the bullet format. Use today's
   date wherever the spec references [DATE].
2. Do the web research yourself with web search (stories from the past 48 hours)
   across the sources the spec lists. Verify any surprising claim against a
   second source before including it.
3. Write the brief to a temp file (e.g. `/tmp/daily-brief.md`). Begin directly
   with the first `## ` section heading — no title, preamble, or search
   narration. `post_brief.py` prepends the dated header.
4. Post it: `./daily.sh /tmp/daily-brief.md` — the wrapper loads `.env` and posts
   to #daily-trivia via the webhook. (You can also pipe on stdin: `./daily.sh < file`.)
5. Check stdout for the "Posted." confirmation line.
6. If "Posted." appeared, tell the user it posted and to verify in #daily-trivia.
   If the script failed or printed anything unexpected, surface the actual output
   and stop — do NOT claim success.

Be brief. Don't narrate the research. Write the brief, post it, and report.
