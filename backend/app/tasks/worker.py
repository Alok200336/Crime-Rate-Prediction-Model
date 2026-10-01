"""Run a single dedicated scheduler process, separate from API workers."""
import signal, threading
from app.db.init_db import init_db
from app.tasks.scheduler import scheduler, ingestion_job
from app.core.config import settings

if __name__ == "__main__":
    init_db()
    scheduler.add_job(ingestion_job, "interval", minutes=settings.ingestion_interval_minutes, max_instances=1, coalesce=True)
    scheduler.start()
    ingestion_job()
    done = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: done.set())
    signal.signal(signal.SIGINT, lambda *_: done.set())
    done.wait()
    scheduler.shutdown()
