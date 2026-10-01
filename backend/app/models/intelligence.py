"""Additive v2 tables: original article and incident columns remain intact."""
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Text, JSON, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def now(): return datetime.now(timezone.utc)

class ArticleIncidentLink(Base):
    __tablename__ = "article_incident_links"
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"), primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("crime_incidents.id"), primary_key=True)
    method: Mapped[str] = mapped_column(String(60), default="primary")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

class IncidentCategory(Base):
    __tablename__ = "incident_categories"
    incident_id: Mapped[int] = mapped_column(ForeignKey("crime_incidents.id"), primary_key=True)
    category: Mapped[str] = mapped_column(String(100), primary_key=True)

class ArticleAssessment(Base):
    __tablename__ = "article_assessments"
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"), primary_key=True)
    disposition: Mapped[str] = mapped_column(String(40), index=True)
    reason: Mapped[str] = mapped_column(Text)
    categories: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    version: Mapped[str] = mapped_column(String(40), default="rules-v2")

class PipelineLog(Base):
    __tablename__ = "pipeline_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="running")
    counts: Mapped[dict] = mapped_column(JSON, default=dict)
    errors: Mapped[list] = mapped_column(JSON, default=list)
