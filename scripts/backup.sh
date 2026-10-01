#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
backup_file="backups/crime-$(date +%Y%m%d-%H%M%S).sql"
docker compose exec -T db pg_dump -U crime -d crime_intelligence > "$backup_file"
printf 'Database backup saved: %s\n' "$backup_file"
