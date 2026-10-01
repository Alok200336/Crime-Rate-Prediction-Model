# Validation record

Upgrade validation, 5 October 2026 (India time).

- Backend: 13 tests passed on Python 3.12 and SQLite.
- Frontend: Vite production build passed; chart and map chunks split successfully.
- Shell scripts: Bash syntax checks passed.
- Live RSS: NDTV India and Times of India India endpoints each returned HTTP 200
  and 20 parseable entries. A separate temporary database ingested all 40 articles:
  0 automatic incidents, 2 pending reviews, 38 excluded; no pipeline errors.
  Those article contents and the test database are NOT included in this ZIP.
  Zero automatic incidents is a valid result of conservative classification, not demo fallback.
- Docker, PostgreSQL and Redis were not integration-tested in this environment.
- Automated browser visual/interaction testing could not run: Chromium download failed.
- NewsAPI collection was not live-tested because no NewsAPI key was supplied.
- No claims are made about classification accuracy, representative crime rates, semantic
  deduplication quality, high-volume capacity, or predictive-model accuracy.

Reproduce backend checks: `cd backend && python -m pytest -q` after installing
`requirements.lock`. Reproduce frontend build: `cd frontend && npm ci && npm run build`.
