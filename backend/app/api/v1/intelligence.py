from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Literal
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_, exists
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import require_admin_key
from app.core.config import settings
from app.models.crime_incident import CrimeIncident as I
from app.models.news_article import NewsArticle as A
from app.models.intelligence import ArticleIncidentLink as L, IncidentCategory as C, ArticleAssessment as R, PipelineLog
from app.services.crime_classifier import CRIME_KEYWORDS
from app.utils.serializers import incident_to_dict

router = APIRouter(tags=["intelligence-v2"])
IST = ZoneInfo("Asia/Kolkata")

class Filters:
    def __init__(self, q: str = Query("", max_length=200), category: str | None = None, state: str | None = None, district: str | None = None, source: str | None = None, start: date | None = None, end: date | None = None, min_confidence: float = Query(0, ge=0, le=1), min_severity: int = Query(1, ge=1, le=5)):
        if start and end and start > end: raise HTTPException(422, "Start date must precede end date")
        self.values = locals().copy(); self.values.pop("self")
    def query(self):
        v = self.values
        stmt = select(I).join(A, I.article_id == A.id).where(~A.url.like("https://example.invalid/%"))
        if v["q"]:
            term = "%" + v["q"].replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
            stmt = stmt.where(or_(I.title.ilike(term, escape="!"), I.summary.ilike(term, escape="!"), I.city.ilike(term, escape="!")))
        if v["category"]: stmt = stmt.where(or_(I.crime_type == v["category"], exists(select(C.incident_id).where(C.incident_id == I.id, C.category == v["category"]))))
        for field in ("state", "district"):
            if v[field]: stmt = stmt.where(getattr(I, field) == v[field])
        if v["source"]: stmt = stmt.where(exists(select(L.article_id).join(A, A.id == L.article_id).where(L.incident_id == I.id, A.source_name == v["source"])))
        if v["start"]: stmt = stmt.where(I.created_at >= datetime.combine(v["start"], time.min, IST).astimezone(timezone.utc))
        if v["end"]: stmt = stmt.where(I.created_at < datetime.combine(v["end"]+timedelta(days=1), time.min, IST).astimezone(timezone.utc))
        return stmt.where(I.confidence_score >= v["min_confidence"], I.severity_score >= v["min_severity"])

def records(db, rows):
    ids = [r.id for r in rows]
    categories = {}; sources = {}
    if ids:
        for i, c in db.execute(select(C.incident_id, C.category).where(C.incident_id.in_(ids))): categories.setdefault(i, []).append(c)
        for link, article in db.execute(select(L, A).join(A, L.article_id == A.id).where(L.incident_id.in_(ids))):
            sources.setdefault(link.incident_id, []).append({"article_id": article.id, "name": article.source_name, "url": article.url, "published_at": article.published_at, "method": link.method})
    out = []
    for row in rows:
        item = incident_to_dict(row)
        item.update(categories=categories.get(row.id, [row.crime_type]), sources=sources.get(row.id, []), location_precision="city centroid" if row.latitude is not None else "unknown", confidence_method="uncalibrated rule score", legacy=db.get(R, row.article_id) is None)
        out.append(item)
    return out

@router.get("/crimes")
@router.get("/latest")
def crimes(filters: Filters = Depends(), limit: int = Query(30, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = filters.query()
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = list(db.scalars(stmt.order_by(I.created_at.desc(), I.id.desc()).offset(offset).limit(limit)))
    return {"items": records(db, rows), "total": total, "limit": limit, "offset": offset}

@router.get("/catalog")
def catalog(db: Session = Depends(get_db)):
    locations = db.execute(select(I.state, I.district).join(A, A.id == I.article_id).where(I.state.is_not(None), ~A.url.like("https://example.invalid/%")).distinct().order_by(I.state, I.district)).all()
    return {"categories": list(CRIME_KEYWORDS), "locations": [{"state": s, "district": d} for s,d in locations], "sources": list(db.scalars(select(A.source_name).where(A.source_name.is_not(None), ~A.url.like("https://example.invalid/%")).distinct().order_by(A.source_name)))}

@router.get("/statistics")
def statistics(filters: Filters = Depends(), period: Literal["day", "week", "month"] = "day", db: Session = Depends(get_db)):
    sub = filters.query().subquery()
    total = db.scalar(select(func.count()).select_from(sub)) or 0
    midnight = datetime.combine(datetime.now(IST).date(), time.min, IST).astimezone(timezone.utc)
    today = db.scalar(select(func.count()).select_from(sub).where(sub.c.created_at >= midnight)) or 0
    def groups(field):
        return [{"name": n or "Unknown", "count": c} for n,c in db.execute(select(field, func.count()).select_from(sub).group_by(field).order_by(func.count().desc()))]
    local = func.timezone("Asia/Kolkata", sub.c.created_at) if db.bind.dialect.name == "postgresql" else func.datetime(sub.c.created_at, "+5 hours", "+30 minutes")
    day = func.date(local)
    trend = {}
    for d,n in db.execute(select(day, func.count()).select_from(sub).group_by(day).order_by(day)):
        dt = date.fromisoformat(str(d))
        key = dt if period == "day" else dt-timedelta(days=dt.weekday()) if period == "week" else dt.replace(day=1)
        trend[str(key)] = trend.get(str(key), 0)+n
    source_rows = db.execute(select(A.source_name, func.count(func.distinct(A.id))).join(L, L.article_id == A.id).where(L.incident_id.in_(select(sub.c.id))).group_by(A.source_name).order_by(func.count(func.distinct(A.id)).desc())).all()
    return {"total_incidents": total, "incidents_today": today, "states_covered": db.scalar(select(func.count(func.distinct(sub.c.state)))), "articles": sum(c for _,c in source_rows), "categories": groups(sub.c.crime_type), "states": groups(sub.c.state), "districts": groups(sub.c.district), "sources": [{"name": n or "Unknown", "count": c} for n,c in source_rows], "trend": [{"date": d, "count": n} for d,n in sorted(trend.items())], "time_basis": "First observed in this database, Asia/Kolkata; not incident occurrence date", "period": period}

@router.get("/states")
def states(filters: Filters = Depends(), db: Session = Depends(get_db)):
    return statistics(filters, "day", db)["states"]

@router.get("/trending")
def trending(filters: Filters = Depends(), db: Session = Depends(get_db)):
    return statistics(filters, "day", db)["categories"]

@router.get("/map")
def map_data(filters: Filters = Depends(), level: Literal["state", "district"] = "district", db: Session = Depends(get_db)):
    sub = filters.query().subquery()
    fields = [sub.c.state] + ([sub.c.district] if level == "district" else [])
    rows = db.execute(select(*fields, func.avg(sub.c.latitude), func.avg(sub.c.longitude), func.count()).where(sub.c.latitude.is_not(None), sub.c.longitude.is_not(None)).group_by(*fields)).all()
    return {"precision": "Approximate aggregation of extracted city centroids; not incident coordinates or official administrative centroids", "items": [{"name": " / ".join(x or "Unknown" for x in row[:-3]), "latitude": row[-3], "longitude": row[-2], "count": row[-1]} for row in rows]}

@router.get("/news")
def news(limit: int = Query(30, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = select(A, R).outerjoin(R, R.article_id == A.id).where(~A.url.like("https://example.invalid/%"), or_(R.disposition.in_(["incident", "linked", "review"]), exists(select(I.id).where(I.article_id == A.id))))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.execute(stmt.order_by(A.published_at.desc().nullslast(), A.id.desc()).offset(offset).limit(limit))
    return {"total": total, "items": [{"id": a.id, "title": a.title, "summary": a.summary, "source_name": a.source_name, "url": a.url, "published_at": a.published_at, "disposition": r.disposition if r else "legacy"} for a,r in rows]}

@router.get("/pipeline", dependencies=[Depends(require_admin_key)])
def pipeline(db: Session = Depends(get_db)):
    logs = db.scalars(select(PipelineLog).order_by(PipelineLog.id.desc()).limit(20))
    queue = db.execute(select(A, R).join(R, R.article_id == A.id).where(R.disposition == "review").order_by(A.id.desc()).limit(100))
    return {"rss_sources": len(settings.rss_feed_list), "newsapi_configured": bool(settings.newsapi_key), "interval_minutes": settings.ingestion_interval_minutes, "runs": [{"id": x.id, "started_at": x.started_at, "finished_at": x.finished_at, "status": x.status, "counts": x.counts, "errors": x.errors} for x in logs], "review": [{"article_id": a.id, "title": a.title, "url": a.url, "reason": r.reason} for a,r in queue]}

class ReviewDecision(BaseModel):
    action: Literal["exclude", "link", "create"]
    incident_id: int | None = None
    categories: list[str] = Field(default_factory=list, max_length=24)
    state: str | None = Field(None, max_length=120)
    district: str | None = Field(None, max_length=120)
    city: str | None = Field(None, max_length=120)
    incident_date: date | None = None

@router.post("/review/{article_id}", dependencies=[Depends(require_admin_key)])
def review(article_id: int, decision: ReviewDecision, db: Session = Depends(get_db)):
    assessment = db.scalar(select(R).where(R.article_id == article_id).with_for_update())
    if not assessment or assessment.disposition != "review": raise HTTPException(404, "Pending review not found")
    if decision.action == "link":
        if not decision.incident_id or not db.get(I, decision.incident_id): raise HTTPException(422, "Existing incident ID required")
        db.add(L(article_id=article_id, incident_id=decision.incident_id, method="human-review", confidence=1))
    if decision.action == "create":
        if not decision.categories or any(c not in CRIME_KEYWORDS for c in decision.categories) or not decision.state or not decision.state.strip():
            raise HTTPException(422, "A valid category and evidence-backed Indian state are required")
        from app.services.crime_extractor import extract_crime_details
        from app.services.deduplication import make_dedupe_key
        a = db.get(A, article_id)
        extracted = extract_crime_details(a.title, a.summary)
        incident = I(article_id=a.id, title=a.title, summary=a.summary, crime_type=decision.categories[0], state=decision.state.strip(), district=decision.district, city=decision.city, incident_date=decision.incident_date, case_status=extracted.case_status, allegation_status=extracted.allegation_status, confidence_score=assessment.confidence, severity_score=max(CRIME_KEYWORDS[c][1] for c in decision.categories), dedupe_key=make_dedupe_key(a.title))
        db.add(incident); db.flush()
        db.add(L(article_id=a.id, incident_id=incident.id, method="human-review"))
        for c in set(decision.categories): db.add(C(incident_id=incident.id, category=c))
    assessment.disposition = {"link": "linked", "create": "incident", "exclude": "excluded"}[decision.action]
    assessment.reason = "Admin review: " + decision.action
    db.commit()
    return {"status": assessment.disposition}
