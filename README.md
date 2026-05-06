# trivia-bot

Generates pub-trivia news briefs and posts them to Discord on a schedule.

## Schedule (Sydney time)
- **Mon/Wed/Fri 5pm** — daily intake → `#daily-trivia`
- **Tue 6pm** — weekly compile (reads `#daily-trivia` history + fresh Tue sweep) → `#trivia-report`

## Setup

### 1. Discord
1. Create two channels on your server: `#daily-trivia` and `#trivia-report`.
2. **Webhooks:** in each channel's settings → Integrations → Webhooks → New Webhook. Copy the URL.
3. **Bot** (only needed for the Tuesday compile to read `#daily-trivia` history):
   - Discord Developer Portal → New Application → Bot tab → Reset Token (copy it).
   - Under Bot → Privileged Gateway Intents, enable **Message Content Intent**.
   - OAuth2 → URL Generator → scope `bot`, permissions `Read Message History` and `View Channels`. Open the generated URL and invite the bot to your server.
   - Right-click `#daily-trivia` → Copy Channel ID (need Developer Mode on in Discord settings → Advanced).

### 2. GitHub repo
1. Push these files to a private repo.
2. Settings → Secrets and variables → Actions → New repository secret. Add:
   - `ANTHROPIC_API_KEY`
   - `DISCORD_WEBHOOK_DAILY`
   - `DISCORD_WEBHOOK_COMPILE`
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_DAILY_CHANNEL_ID`

### 3. Verify before going live
Both workflows have `workflow_dispatch` — fire them manually from the Actions tab to confirm posting works. The script self-checks Sydney wall time and exits silently if it's not the right day/hour, so a manual run outside the window will succeed but post nothing. To do a true end-to-end test, temporarily comment out the `in_intake_window` / `in_compile_window` check, run, then re-enable.

## Things worth knowing
- **DST handling:** GitHub Actions cron is UTC. Each workflow has two cron entries (one for AEST, one for AEDT). Both fire; the script self-checks Sydney wall time and only one run does real work. No manual cron updates twice a year.
- **Cost estimate:** ~4 API calls per week, ~5-8k input tokens + web_search + ~1-4k output. Roughly USD $1-3/week at Opus pricing, less if you swap to Sonnet (`claude-sonnet-4-6` in the MODEL constant).
- **Failure mode:** silent. If a run fails, check the Actions tab. No alerting wired up.
- **Verify before deploying:** model string (`claude-opus-4-7`) and web_search tool version (`web_search_20250305`) — Anthropic ships new versions occasionally; check current docs at https://docs.claude.com.
