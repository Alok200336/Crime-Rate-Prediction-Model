#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "This removes the PostgreSQL volume and all local project data."
docker compose down -v
