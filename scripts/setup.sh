#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
fi
python3 - <<'PYSETUP'
from pathlib import Path
import secrets
p = Path('backend/.env')
s = p.read_text()
lines = s.splitlines()
value = next((line.split('=',1)[1].strip() for line in lines if line.startswith('ADMIN_API_KEY=')), '')
if not value or value == 'change-me':
    lines = [line for line in lines if not line.startswith('ADMIN_API_KEY=')]
    lines.append('ADMIN_API_KEY=' + secrets.token_urlsafe(32))
if not any(line.startswith('NEWS_RSS_FEEDS=') and line.split('=',1)[1].strip() for line in lines):
    lines = [line for line in lines if not line.startswith('NEWS_RSS_FEEDS=')]
    lines.append(next(line for line in Path('backend/.env.example').read_text().splitlines() if line.startswith('NEWS_RSS_FEEDS=')))
p.write_text('\n'.join(lines) + '\n')
p.chmod(0o600)
print('Configuration ready. Set NEWS_RSS_FEEDS in backend/.env. The admin key is in that file.')
PYSETUP
