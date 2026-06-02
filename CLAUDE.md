# Trivia Bot — Claude Code Context

## What this repo does

Generates light-hearted, trivia-worthy news briefs for a weekly pub trivia
night in Newcastle/Lake Macquarie, NSW, Australia, and posts them to Discord.

**Claude Code does the research and writes the briefs.** The Python scripts no
longer call any model — they only fetch the week's intakes from Discord and post
a finished brief that Claude wrote. The workflow:

- **Daily intake** → Claude researches the last 48 hours (web search), writes a
  brief following `scripts/prompts/daily_intake.txt`, and posts it to
  `#daily-trivia`. Designed for Mon/Wed/Fri ~5pm Sydney, triggered manually.
- **Tuesday compile** → Claude pulls the week's daily intakes from Discord, reads
  last week's Tuesday brief (to drop already-covered stories), does a fresh web
  sweep, and compiles a structured brief following
  `scripts/prompts/tuesday_compile.txt` (sections: news brief, celebrity
  birthdays, this month in history, on this day, today's special day when
  applicable, and the Quizmasters "Fans & Followers" question). Posts to
  `#trivia-report`. Designed for Tuesday ~6pm Sydney, triggered manually.

## The two commands

The `/daily` and `/tuesday` slash commands (in `.claude/commands/`) drive the
whole flow — they tell Claude to research, write the brief, and post it. Each
ends by posting through a thin wrapper:

```bash
./daily.sh   BRIEF_FILE   # or: ./daily.sh   < brief.md   → posts to #daily-trivia
./tuesday.sh BRIEF_FILE   # or: ./tuesday.sh < brief.md   → posts to #trivia-report
```

Both wrappers:
- Load secrets from `.env` (gitignored)
- Use `.venv/bin/python` if it exists, otherwise the system `python3`
- Call `scripts/post_brief.py {daily|weekly} <brief>`, which prepends a dated
  header, chunks the text under Discord's 2000-char limit, and posts via the
  channel webhook. It prints `Posted.` on success.

There is **no** time-of-day guard and **no** Anthropic API key — the scripts just
fetch and post.

## Prerequisites (already done — don't redo unless setting up fresh)

- `.venv/` exists with `requirements.txt` installed (`requests` only)
- `.env` exists and contains all four secrets (see `.env.example`):
  `DISCORD_WEBHOOK_DAILY`, `DISCORD_WEBHOOK_WEEKLY`, `DISCORD_BOT_TOKEN_DAILY`,
  `DISCORD_DAILY_CHANNEL_ID`
- `daily.sh` and `tuesday.sh` are executable

## Key files

```
.claude/commands/
├── daily.md               # /daily — research + write + post the daily intake
└── tuesday.md             # /tuesday — compile + post the weekly brief
scripts/
├── post_brief.py          # posts a Claude-written brief to Discord (daily|weekly)
├── fetch_intakes.py       # prints the week's #daily-trivia intakes (Tuesday input)
└── prompts/
    ├── daily_intake.txt    # spec Claude follows to write the daily intake
    └── tuesday_compile.txt # spec for the Tuesday brief ([DATE] / [INTAKES] placeholders)
daily.sh                   # wrapper: load .env, post_brief.py daily
tuesday.sh                 # wrapper: load .env, post_brief.py weekly
.env                       # secrets (gitignored)
.env.example               # template showing which secrets are needed
```

## Output format and tone — what "good" looks like

- 60% Australian content, 40% global
- Each bullet must have a clean named/numbered answer (a name, a number, a
  place, a date). Vague entries are dropped (hard filter in the prompt specs).
- Excludes: deaths, fatal accidents, war casualties, sexual assault, cold
  cases. Historical "on this day" anniversaries are exempt from the exclude
  list.
- No editorial commentary ("a classic trivia answer", "useful question")

## Common things you might be asked to do

- **"Fire the daily"** → run `/daily`: research, write the brief, post via
  `./daily.sh`, and confirm the `Posted.` line appeared in stdout.
- **"Fire the Tuesday compile"** → run `/tuesday` likewise (posts via
  `./tuesday.sh`).
- **"Tweak the prompt"** → edit `scripts/prompts/daily_intake.txt` or
  `scripts/prompts/tuesday_compile.txt`. Propose the diff first rather than
  rewriting wholesale. After edits, commit with a descriptive message and push.
- **"Look at the output"** — check the Discord channel directly; the post step
  only prints `Posted.` (and per-chunk HTTP status) to stdout.

## Things to flag honestly

- If the post step succeeds but Discord shows nothing, the webhook URL in
  `.env` may be invalid or pointing at the wrong channel. Don't claim it
  posted unless you saw `Posted.` in stdout and the user confirms Discord.
- The prompt files are tuned iteratively. If asked to change them, propose
  the diff first rather than rewriting wholesale.
- `fetch_intakes.py` fetches the last 20 messages from `#daily-trivia` and does
  NOT filter to bot-authored messages, so user replies in that channel get
  included as Tuesday-compile input and could in principle influence output
  (mild prompt-injection risk). A bot-author filter is the proper fix but
  hasn't been done yet.
- Reading last week's Tuesday brief for dedup uses the daily bot token against
  the `#trivia-report` channel id — never print the token.
