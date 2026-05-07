#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
