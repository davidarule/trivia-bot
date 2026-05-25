# Trivia Bot — Claude Code Context

## What this repo does

Generates light-hearted, trivia-worthy news briefs for a weekly pub trivia
night in Newcastle/Lake Macquarie, NSW, Australia. Two scripts drive it:

- **`scripts/daily_intake.py`** — a quick intake of trivia-worthy stories from
  the last 48 hours, posted to the `#daily-trivia` Discord channel. Designed
  to fire Mon/Wed/Fri at 5pm Sydney time, but now triggered manually from this
  Mac.
- **`scripts/tuesday_compile.py`** — pulls the week's daily intakes from the
  Discord channel history, does a fresh web sweep, and compiles a structured
  trivia brief (5 sections: news brief, celebrity birthdays, this month in
  history (first Tue of month only), on this day). Posts to `#trivia-report`.
  Designed for Tuesday 6pm Sydney; triggered manually from this Mac.

Both scripts use the Anthropic API with the `web_search` tool to find current
stories, then post to Discord via webhooks.

## The two commands

```bash
./daily.sh      # fire the daily intake, posts to #daily-trivia
./tuesday.sh    # fire the Tuesday compile, posts to #trivia-report
```

Both wrappers:
- Load secrets from `.env` (gitignored)
- Set `TRIVIA_FORCE_RUN=1` to bypass the Sydney time-of-day guard built into
  the Python scripts
- Use `.venv/bin/python` if it exists, otherwise the system `python3`

## Prerequisites (already done — don't redo unless setting up fresh)

- `.venv/` exists with `requirements.txt` installed
- `.env` exists and contains all five secrets (see `.env.example`)
- `daily.sh` and `tuesday.sh` are executable

## Key files

```
scripts/
├── daily_intake.py        # entry point for daily intake
├── tuesday_compile.py     # entry point for Tuesday compile
└── prompts/
    ├── daily_intake.txt   # prompt for the daily intake
    └── tuesday_compile.txt # prompt for the Tuesday compile (with [DATE],
                            # [INTAKES], [INCLUDE_MONTH_HISTORY] placeholders)
daily.sh                   # wrapper to run daily_intake.py
tuesday.sh                 # wrapper to run tuesday_compile.py
.env                       # secrets (gitignored)
.env.example               # template showing which secrets are needed
.github/workflows/         # GitHub Actions workflows — schedule disabled,
                            # kept as break-glass fallback only
```

## Output format and tone — what "good" looks like

- 60% Australian content, 40% global
- Each bullet must have a clean named/numbered answer (a name, a number, a
  place, a date). Vague entries are filtered out by the prompt.
- Excludes: deaths, fatal accidents, war casualties, sexual assault, cold
  cases. Historical "on this day" anniversaries are exempt from the exclude
  list.
- No editorial commentary ("a classic trivia answer", "useful question")

## Common things you might be asked to do

- **"Fire the daily"** → run `./daily.sh` and confirm whether the
  "Posted." line appeared in stdout.
- **"Fire the Tuesday compile"** → run `./tuesday.sh` likewise.
- **"Tweak the prompt"** → edit `scripts/prompts/daily_intake.txt` or
  `scripts/prompts/tuesday_compile.txt`. After edits, commit with a
  descriptive message and push.
- **"Look at the output"** — check the Discord channel directly; the script
  only prints "Posted." to stdout.

## Things to flag honestly

- If `./daily.sh` succeeds but Discord shows nothing, the webhook URL in
  `.env` may be invalid or pointing at the wrong channel. Don't claim it
  posted unless you saw "Posted." in stdout and the user confirms Discord.
- The prompt files are tuned iteratively. If asked to change them, propose
  the diff first (or use dry-run) rather than rewriting wholesale.
- The Tuesday compile fetches the last 20 messages from `#daily-trivia`. It
  does NOT currently filter to bot-authored messages, so user replies in
  that channel get included as data and could in principle influence output
  (mild prompt-injection risk). A bot-author filter in `fetch_recent_intakes`
  is the proper fix but hasn't been done yet.
