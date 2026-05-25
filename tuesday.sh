#!/usr/bin/env bash
# Manual trigger for the Tuesday compile. Loads secrets from .env, bypasses
# the Sydney time-of-day guard, and posts to #trivia-report.
#
# Usage:  ./tuesday.sh

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

TRIVIA_FORCE_RUN=1 "$PY" scripts/tuesday_compile.py
