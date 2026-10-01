#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker CLI is not installed." >&2; exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker Desktop/daemon is not running. Start Docker Desktop first." >&2; exit 1
fi
[ -f backend/.env ] || cp backend/.env.example backend/.env
docker compose up --build
