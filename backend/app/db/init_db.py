from sqlalchemy import select
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import crime_incident, news_article
from app.models.intelligence import ArticleIncidentLink, IncidentCategory


def init_db():
    # Idempotent additive migration, v1 -> v2. No original columns or rows removed.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for incident in db.scalars(select(crime_incident.CrimeIncident)).yield_per(500):
            key = (incident.article_id, incident.id)
            if db.get(ArticleIncidentLink, key) is None:
                db.add(ArticleIncidentLink(article_id=key[0], incident_id=key[1], method="legacy"))
            if db.get(IncidentCategory, (incident.id, incident.crime_type)) is None:
                db.add(IncidentCategory(incident_id=incident.id, category=incident.crime_type))
        db.commit()
