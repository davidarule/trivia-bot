#!/usr/bin/env bash
# Post a Claude-generated Tuesday compile to #trivia-report.
#
# Claude Code reads the week's intakes (scripts/fetch_intakes.py), does a fresh
# web sweep, and writes the brief (following scripts/prompts/tuesday_compile.txt).
# This wrapper loads secrets from .env and posts the brief via the channel webhook.
#
# Usage:  ./tuesday.sh BRIEF_FILE       # post a brief file
#         ./tuesday.sh < brief.md       # or pipe the brief on stdin

set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "Error: .env not found. Copy .env.example to .env and fill in secrets." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
else
  PY=$(command -v python3 || command -v python)
fi

"$PY" scripts/post_brief.py weekly "$@"
