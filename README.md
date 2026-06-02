# trivia-bot

Generates pub-trivia news briefs and posts them to Discord. **Claude Code does
the research and writes the briefs**; the Python scripts only fetch the week's
intakes from Discord and post a finished brief.

Two flows, triggered manually from a local machine via slash commands:

- **Daily intake** (`/daily` → `./daily.sh`) — Claude researches the last 48
  hours and posts a short intake to `#daily-trivia`. Run Mon/Wed/Fri.
- **Weekly compile** (`/tuesday` → `./tuesday.sh`) — Claude pulls the week's
  `#daily-trivia` intakes, drops anything covered in last week's brief, does a
  fresh web sweep, and posts a structured brief to `#trivia-report`. Run Tue.

## How it works

1. `/daily` or `/tuesday` (defined in `.claude/commands/`) tells Claude to
   research and write the brief, following the spec in `scripts/prompts/`.
2. Claude writes the brief to a file and posts it via the wrapper:
   `./daily.sh BRIEF_FILE` or `./tuesday.sh BRIEF_FILE` (stdin also works).
3. The wrapper loads `.env` and runs `scripts/post_brief.py`, which prepends a
   dated header, chunks the text under Discord's 2000-char limit, posts via the
   channel webhook, and prints `Posted.`.
4. For the Tuesday compile, `scripts/fetch_intakes.py` prints the week's
   `#daily-trivia` messages as Claude's primary input.

## Setup

### 1. Discord
1. Create two channels on your server: `#daily-trivia` and `#trivia-report`.
2. **Webhooks:** in each channel's settings → Integrations → Webhooks → New
   Webhook. Copy the URL for each.
3. **Bot** (only needed so the Tuesday compile can read channel history):
   - Discord Developer Portal → New Application → Bot tab → Reset Token (copy it).
   - Under Bot → Privileged Gateway Intents, enable **Message Content Intent**.
   - OAuth2 → URL Generator → scope `bot`, permissions `Read Message History`
     and `View Channels`. Open the generated URL and invite the bot to your server.
   - Right-click `#daily-trivia` → Copy Channel ID (enable Developer Mode in
     Discord settings → Advanced first).

### 2. Local environment
1. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
   (only dependency is `requests`).
2. Copy `.env.example` to `.env` and fill in the four secrets:
   - `DISCORD_WEBHOOK_DAILY` — webhook for `#daily-trivia`
   - `DISCORD_WEBHOOK_WEEKLY` — webhook for `#trivia-report`
   - `DISCORD_BOT_TOKEN_DAILY` — bot token (reads channel history)
   - `DISCORD_DAILY_CHANNEL_ID` — `#daily-trivia` channel id
3. `chmod +x daily.sh tuesday.sh` if they aren't already executable.

`.env` is gitignored — secrets stay local.

## Running it

From the repo root, in Claude Code:

- `/daily` — fire the daily intake (posts to `#daily-trivia`).
- `/tuesday` — fire the weekly compile (posts to `#trivia-report`).

Each command researches, writes the brief, posts it, and reports whether
`Posted.` appeared in stdout.

## Things worth knowing

- **No model runs in CI or in the scripts.** The brief is written by Claude Code
  interactively. There is no scheduler and no API key — runs are manual.
- **Tone and filters** live in `scripts/prompts/*.txt`: ~60/40 Australian/global,
  every bullet needs a clean named/numbered answer, and a mandatory exclude list
  (deaths, fatal accidents, war, assault, cold cases). Edit the prompt files to
  tune output.
- **Verify before claiming success:** the post step only prints `Posted.` plus
  per-chunk HTTP status. If nothing appears in Discord, check the webhook URL.
