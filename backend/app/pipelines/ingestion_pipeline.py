import threading
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.core.config import settings
from app.models.crime_incident import CrimeIncident
from app.models.news_article import NewsArticle
from app.models.intelligence import ArticleAssessment, ArticleIncidentLink, IncidentCategory, PipelineLog
from app.services.crime_classifier import classify_crime
from app.services.crime_extractor import extract_crime_details
from app.services.deduplication import make_dedupe_key, canonical_url

_local_lock = threading.Lock()


def run_ingestion(db, collector):
    lock = None
    if settings.redis_url:
        import redis
        lock = redis.Redis.from_url(settings.redis_url).lock("crime-ingestion-v2", timeout=3600, blocking_timeout=0)
    else: lock = _local_lock
    if not lock.acquire(blocking=False): return {"status": "busy"}
    try: return _run(db, collector, lock if settings.redis_url else None)
    finally: lock.release()


def _run(db, collector, lease=None):
    log = PipelineLog(); db.add(log); db.commit()
    counts = dict(fetched=0, new_articles=0, new_incidents=0, duplicate_articles=0, review=0, excluded=0)
    errors = []
    try:
        fetched = collector.fetch(); errors.extend(getattr(collector, "errors", [])); counts["fetched"] = len(fetched)
        for payload in fetched:
            if lease: lease.extend(3600, replace_ttl=True)
            try:
                url = canonical_url(payload.url)
                article = db.scalar(select(NewsArticle).where(NewsArticle.url == url))
                if article and article.processed: continue
                new_article = article is None
                if new_article:
                    article = NewsArticle(title=payload.title[:500], summary=(payload.summary or "")[:1200], source_name=payload.source_name, url=url, published_at=payload.published_at)
                    db.add(article); db.flush()
                c = classify_crime(article.title, article.summary)
                extracted = extract_crime_details(article.title, article.summary)
                disposition, reason = c.disposition, c.reason
                if disposition == "candidate" and not extracted.state:
                    disposition, reason = "review", "Unknown or ambiguous India location"
                key = make_dedupe_key(article.title)
                match = None
                # Only exact normalized titles, a matching city, and close known publication dates.
                if c.is_crime and article.published_at and extracted.city:
                    match = db.scalar(select(CrimeIncident).join(NewsArticle, CrimeIncident.article_id == NewsArticle.id).where(CrimeIncident.dedupe_key == key, CrimeIncident.city == extracted.city, NewsArticle.published_at.between(article.published_at-timedelta(hours=48), article.published_at+timedelta(hours=48))).limit(1))
                if match:
                    db.add(ArticleIncidentLink(article_id=article.id, incident_id=match.id, method="exact-title-city-time", confidence=.85))
                    disposition, reason = "linked", "Conservative exact-title cluster; reviewer can audit original sources"
                elif disposition == "candidate":
                    incident = CrimeIncident(article_id=article.id, title=article.title, summary=article.summary, crime_type=c.crime_type, confidence_score=c.confidence, severity_score=c.severity_score, dedupe_key=key, **vars(extracted))
                    db.add(incident); db.flush()
                    db.add(ArticleIncidentLink(article_id=article.id, incident_id=incident.id))
                    for category in c.categories: db.add(IncidentCategory(incident_id=incident.id, category=category))
                    disposition = "incident"
                db.add(ArticleAssessment(article_id=article.id, disposition=disposition, reason=reason, categories=c.categories, confidence=c.confidence))
                article.processed = True
                db.commit()
                counts["new_articles"] += int(new_article)
                if disposition == "incident": counts["new_incidents"] += 1
                elif disposition == "linked": counts["duplicate_articles"] += 1
                elif disposition in counts: counts[disposition] += 1
            except Exception as exc:
                db.rollback(); errors.append(f"Article processing: {type(exc).__name__}")
        log = db.get(PipelineLog, log.id)
        log.status = "partial" if errors else "success"
    except Exception as exc:
        db.rollback(); log = db.get(PipelineLog, log.id); log.status = "failed"; errors.append(type(exc).__name__)
    log.counts = counts; log.errors = errors; log.finished_at = datetime.now(timezone.utc); db.commit()
    return {**counts, "status": log.status, "errors": errors}
