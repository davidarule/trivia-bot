#!/usr/bin/env bash
# Post a Claude-generated daily intake to #daily-trivia.
#
# Claude Code does the web research and writes the brief (following
# scripts/prompts/daily_intake.txt). This wrapper loads secrets from .env and
# posts the brief via the channel webhook.
#
# Usage:  ./daily.sh BRIEF_FILE         # post a brief file
#         ./daily.sh < brief.md         # or pipe the brief on stdin

set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "Error: .env not found. Copy .env.example to .env and fill in secrets." >&2
  exit 1
fi

# Load .env without leaking values to stderr
set -a
# shellcheck disable=SC1091
source .env
set +a

# Pick the python interpreter — prefer .venv if present
if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
else
  PY=$(command -v python3 || command -v python)
fi

"$PY" scripts/post_brief.py daily "$@"
