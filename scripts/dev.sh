#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

check_port() {
  if ! nc -z localhost "$1" 2>/dev/null; then
    echo "WARNING: nothing listening on localhost:$1 ($2). Start it before continuing." >&2
  fi
}

check_port 27017 "MongoDB"
check_port 6379 "Redis"

trap 'kill 0' EXIT

( cd "$ROOT/backend" && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000 ) &
( cd "$ROOT/worker" && source .venv/bin/activate && arq worker.WorkerSettings ) &
( cd "$ROOT/frontend" && npm run dev ) &

wait
