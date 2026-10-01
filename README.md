# Crime Intelligence India — v2 upgrade

A local research application for **news-derived crime incidents and reporting trends in India**.
Upgraded from the uploaded FastAPI/PostgreSQL/Streamlit project. React + Tailwind is now
the primary dashboard; the original Streamlit dashboard remains available as an optional legacy interface.

## Upgrade your existing installation safely

The ZIP contains code, not your Mac's database or private `.env` file.
Keep using the **same existing project directory and Compose project name** so Docker
reuses your existing `postgres_data` volume. Do not use `docker compose down -v`.

1. In your existing `crime-intelligence-india-working` folder, with the database running:

   ```bash
   mkdir -p backups
   docker compose exec -T db pg_dump -U crime -d crime_intelligence > backups/before-v2.sql
   ```

   Confirm the command succeeds and the backup is nonempty before proceeding.
   If you previously used `docker compose -p NAME`, use that same `-p NAME` on every command.

2. Extract this ZIP into a **separate temporary folder**. Copy its contents into your existing
   project, preserving your `.env`, `.git`, and backups. From the old project directory:

   ```bash
   rsync -av --exclude='.env' --exclude='.git/' --exclude='backups/' \
     /path/to/extracted/crime-intelligence-india-working/ ./
   ```

   Replace `/path/to/extracted/` with the real extraction path. Do not use `--delete`.
   If you have code edits newer than the uploaded ZIP, back those up before copying.

3. Prepare configuration and rebuild:

   ```bash
   bash scripts/setup.sh
   docker compose up --build -d
   docker compose ps
   ```

   Setup preserves existing settings and generates an admin key only if absent/default.
   It adds starter RSS sources only if your feed setting is missing or blank.
   Existing original rows remain intact. Startup adds link/category/assessment/log tables
   and backfills links and primary categories for legacy incidents. No schema columns are dropped.
   Existing legacy incidents are not silently reclassified or reclustered.

4. Open **http://localhost:3000**. API documentation: **http://localhost:8000/docs**.
   Open `backend/.env` locally, copy `ADMIN_API_KEY`, and enter it in **Pipeline Admin**.
   Select **Load status** or **Collect news now**. The worker also collects at startup
   and every `INGESTION_INTERVAL_MINUTES` (60 by default).

5. Optional old dashboard:

   ```bash
   docker compose --profile legacy up -d dashboard
   ```

   Open http://localhost:8501. Enter the admin key in the Pipeline Admin sidebar.
   New review, source-link, demo-exclusion and IST analytics semantics are implemented
   in the React dashboard. Legacy analytics retain v1 semantics and may include old demos.

### Fresh installation

Enter the extracted `crime-intelligence-india-working` directory and run:

```bash
bash scripts/setup.sh
docker compose up --build -d
```

Docker Desktop must be running. No host PostgreSQL installation is needed. PostgreSQL
and Redis ports are internal, avoiding the old host port 5432 conflict. Web/API ports
bind to localhost. The bundled `crime` database password preserves v1 local compatibility;
this Compose configuration is **not a public production deployment**.

## What changed

- React/Tailwind dashboard: overview, live feed, latest crime reporting, analytics,
  state/district aggregate maps and pipeline administration; responsive layout.
- All 24 requested categories, with multiple categories per incident.
- Search, source/category/state/district/date/confidence/severity filters and pagination.
- Day/week/month trends; first-observed-today count uses **Asia/Kolkata**.
- Bounded RSS/Atom requests with per-source error isolation; optional NewsAPI adapter.
- Separate article and incident records; linked duplicate reports remain accessible.
- Review queue for court/historical/aggregate coverage, ambiguous locations, weak event
  evidence and negated/non-criminal contexts. Admins can exclude, link to an existing
  incident or create an incident using reviewed category/location/date information.
- Per-run ingestion logs, separate scheduled worker and Redis cross-process ingestion lock.
- Demo seeding is disabled by default. Existing `example.invalid` demo rows are preserved
  but excluded from the new public dashboard endpoints.
- Admin endpoints reject blank/default keys. React escapes text; legacy cards now escape
  publisher text as well. Keys are not embedded into the frontend or stored in browser storage.

## Sources and live data

Two starter India RSS feeds are configured in `.env.example`:

- `https://feeds.feedburner.com/ndtvnews-india-news`
- `https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms`

Both returned HTTP 200 and parseable entries during this upgrade. Availability and
content can change. Review the publishers' feed terms for your intended use:
[NDTV RSS](https://www.ndtv.com/rss?site=classic),
[Times of India RSS](https://timesofindia.indiatimes.com/rss_index.cms).
Public feed access does not itself grant permission to republish content commercially.

Set comma-separated `NEWS_RSS_FEEDS` to your permitted sources. Optional `NEWSAPI_KEY`
enables a second collector through NewsAPI's everything endpoint. No API keys are included.
Check [NewsAPI pricing](https://newsapi.org/pricing) and [terms](https://newsapi.org/terms)
for current access and licensing; the app does not bypass plan limitations.
After editing configuration:

```bash
docker compose up -d --force-recreate backend worker
```

Collection reads feed metadata and short supplied excerpts (up to 1,200 characters),
not full publisher pages. The raw article body is not scraped or newly stored.
A feed window can omit older articles; this is not a complete historical archive.
NewsAPI collection currently fetches one page (up to 100 items) per run.
The dashboard refreshes every minute; collection is scheduled, **not a real-time push service**.
No sample incidents are automatically inserted. An empty feed or review-only result is valid.

## Data model and interpretation

Original `news_articles` and `crime_incidents` tables and API routes are retained.
The old `crime_incidents.article_id` remains the primary-report pointer for compatibility.
New tables:

| Table | Purpose |
| --- | --- |
| `article_incident_links` | Many reports supporting an incident, with link method/confidence |
| `incident_categories` | Multiple category labels per incident |
| `article_assessments` | Classification disposition, reason, rule version and score |
| `pipeline_logs` | Run times, status, counts and source/processing errors |

Categories are versioned in code; locations and sources remain on original records.
Statistics are computed from stored rows rather than materialized daily/trend tables.
An incident is a news-derived record, never a finding of guilt. Source reports remain
separate, and alleged/reported/arrested/convicted/acquitted wording is retained where extracted.
An article can be reviewed independently without overwriting the primary report's status.

**Time:** publication time belongs to the source article; first-observed time belongs to
the database record. Automatic incident-date extraction is intentionally not guessed.
Reviewers can supply a supported incident date. All date filters, maps and aggregate
trends in v2 use **first observed**, not the date of the alleged event. Weekly buckets
start Monday; monthly buckets start on day one. Buckets with no records are omitted.

**Location:** the bundled English gazetteer covers a limited set of cities. Missing or
multiple city matches go to review. Coordinates are approximate city centroids, never
crime-scene coordinates. State/district map circles aggregate available city centroids;
they are not authoritative administrative boundaries or geocoded incident locations.
Manual review does not invent coordinates.

**Deduplication:** automatic linking requires an identical normalized title, the same
extracted city, and publication times within 48 hours. This intentionally conservative
rule misses paraphrases and can still link similar generic headlines incorrectly.
A case update can be linked manually to a known incident. Unknown dates do not auto-merge.
No historic v1 duplicate losses can be recovered without recollecting the original articles.

**Classification:** this release uses English rules, not trained spaCy/transformer/LLM
inference. Extraction scores are uncalibrated rule scores, not truth probabilities.
Severity is a fixed category scale, not a validated harm measure. Articles describing
multiple separate incidents are not automatically split. Human review and measured
precision/recall are required before treating this as a reliable event dataset.

News coverage is geographically and editorially biased. Keep official NCRB data separate.
No trained prediction model was present in the uploaded ZIP; `ml/README.md` describes
how to connect one later. LLM extraction, semantic deduplication, exhaustive location
resolution, public deployment hardening and load testing are future work.

## API (all under `/api/v1`)

| Route | Description |
| --- | --- |
| `GET /crimes`, `/latest` | Paginated incident records with categories and source links |
| `GET /catalog` | Taxonomy, observed locations and sources |
| `GET /statistics?period=day` | Aggregate stats and day/week/month trends |
| `GET /trending`, `/states` | Primary-category and state counts under current filters |
| `GET /map?level=district` | Approximate district/state map aggregations |
| `GET /news` | Latest related articles, including pending review; separate from incident counts |
| `GET /pipeline` | Admin-only logs and newest 100 pending reviews |
| `POST /ingestion/run` | Admin-only immediate collection |
| `POST /review/{article_id}` | Admin-only exclude/link/create review decision |
| `GET /health` | Database connectivity check |

Incident/filter endpoints accept `q`, `category`, `state`, `district`, `source`, `start`,
`end`, `min_confidence`, and `min_severity`. `/crimes` accepts `limit` (max 200) and `offset`.
`/news` has independent pagination and intentionally shows all related source reports.
Admin requests require `X-Admin-Key`. OpenAPI examples and request schemas are at `/docs`.

## Local development and checks

Python 3.12 and Node 22.12+ are suitable for the included dependency set.
Frontend setup follows [Vite](https://vite.dev/guide/) and
[Tailwind's Vite integration](https://tailwindcss.com/docs/installation/using-vite).

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
DATABASE_URL=sqlite:///./local.db REDIS_URL= SCHEDULER_ENABLED=false uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Vite proxies `/api` to localhost:8000. For tests, from `backend`:

```bash
python -m pytest -q
```

Validation from this upgrade:

- 13 backend tests passed on SQLite: taxonomy, word boundaries, ambiguous locations,
  multi-category records, duplicate linking, idempotence, source failures, additive
  backfill, API filters, IST aggregation, admin protection and human review.
- `npm run build` passed, with separate chart/map bundles and a committed npm lockfile.
- Public starter RSS endpoints returned valid feed responses; see `VALIDATION.md` for
  the end-to-end collection result.
- Docker/PostgreSQL/Redis integration was not executed: Docker is unavailable here.
- Browser interaction/visual checks were attempted but could not run because the
  Chromium download failed. Desktop/mobile layout still needs a browser check on your Mac.

## Operations

```bash
docker compose logs --tail=100 backend worker
bash scripts/backup.sh
```

Do not scale the scheduler process without understanding ingestion locking. Redis is
used for the cross-process ingestion lock; aggregate response caching and Celery queues
are not implemented. Running outside Compose without Redis uses an in-process lock only.
Keep ingestion intervals positive and ensure configured feeds are trusted administrator inputs.

This local version does not include user accounts, per-user authorization, public rate
limiting, TLS termination, a dead-letter queue, or tested disaster recovery. Before public
hosting, configure those, rotate local database credentials, review content permissions,
and verify the PostgreSQL migration against a backup copy of your database.
