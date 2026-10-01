from datetime import date, datetime, timedelta, timezone
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.models.crime_incident import CrimeIncident
from app.models.news_article import NewsArticle


def _query():
    return select(CrimeIncident).options(joinedload(CrimeIncident.article))


def latest(db: Session, limit: int = 50):
    return list(db.scalars(_query().order_by(desc(CrimeIncident.created_at)).limit(limit)).all())


def search(db: Session, q: str | None, crime_type: str | None, state: str | None, limit: int = 100):
    stmt = _query()
    if q:
        term = f"%{q}%"
        stmt = stmt.where(or_(CrimeIncident.title.ilike(term), CrimeIncident.summary.ilike(term), CrimeIncident.city.ilike(term)))
    if crime_type:
        stmt = stmt.where(CrimeIncident.crime_type == crime_type)
    if state:
        stmt = stmt.where(CrimeIncident.state == state)
    return list(db.scalars(stmt.order_by(desc(CrimeIncident.created_at)).limit(limit)).unique().all())


def exists_for_article(db: Session, article_id: int) -> bool:
    return db.scalar(select(CrimeIncident.id).where(CrimeIncident.article_id == article_id)) is not None


def similar_recent_exists(db: Session, dedupe_key: str) -> bool:
    since = datetime.now(timezone.utc) - timedelta(days=3)
    return db.scalar(select(CrimeIncident.id).where(CrimeIncident.dedupe_key == dedupe_key, CrimeIncident.created_at >= since)) is not None


def counts_by_field(db: Session, field, days: int = 30, limit: int = 20):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = select(field, func.count(CrimeIncident.id)).where(CrimeIncident.created_at >= since, field.is_not(None)).group_by(field).order_by(desc(func.count(CrimeIncident.id))).limit(limit)
    return [(name, count) for name, count in db.execute(stmt).all()]


def daily_trend(db: Session, days: int = 30):
    since = date.today() - timedelta(days=days - 1)
    day = func.date(CrimeIncident.created_at)
    rows = db.execute(select(day, func.count(CrimeIncident.id)).where(CrimeIncident.created_at >= since).group_by(day).order_by(day)).all()
    return [(str(d), c) for d, c in rows]


def dashboard_stats(db: Session):
    total = db.scalar(select(func.count(CrimeIncident.id))) or 0
    today = date.today()
    today_count = db.scalar(select(func.count(CrimeIncident.id)).where(func.date(CrimeIncident.created_at) == today)) or 0
    states = db.scalar(select(func.count(func.distinct(CrimeIncident.state))).where(CrimeIncident.state.is_not(None))) or 0
    sources = db.scalar(select(func.count(func.distinct(NewsArticle.source_name))).join(CrimeIncident, CrimeIncident.article_id == NewsArticle.id)) or 0
    top = db.execute(select(CrimeIncident.crime_type, func.count(CrimeIncident.id)).group_by(CrimeIncident.crime_type).order_by(desc(func.count(CrimeIncident.id))).limit(1)).first()
    return total, today_count, states, sources, top[0] if top else None
