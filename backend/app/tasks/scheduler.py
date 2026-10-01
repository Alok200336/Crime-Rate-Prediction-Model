import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.collectors.multi_source import MultiSourceCollector
from app.core.config import settings
from app.db.session import SessionLocal
from app.pipelines.ingestion_pipeline import run_ingestion

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def ingestion_job():
    if not settings.rss_feed_list and not settings.newsapi_key:
        logger.info("No NEWS_RSS_FEEDS configured; scheduled ingestion skipped")
        return
    db = SessionLocal()
    try:
        run_ingestion(db, MultiSourceCollector())
    except Exception:
        logger.exception("Scheduled ingestion failed")
    finally:
        db.close()


def start_scheduler():
    if not settings.scheduler_enabled or scheduler.running:
        return
    scheduler.add_job(ingestion_job, "interval", minutes=settings.ingestion_interval_minutes, id="crime-news-ingestion", replace_existing=True)
    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
