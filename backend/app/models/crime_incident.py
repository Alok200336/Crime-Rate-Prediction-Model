from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CrimeIncident(Base):
    __tablename__ = "crime_incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id", ondelete="CASCADE"), unique=True, index=True)
    crime_type: Mapped[str] = mapped_column(String(100), index=True)
    crime_subtype: Mapped[str | None] = mapped_column(String(150), nullable=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    incident_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    district: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    victim_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suspect_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    case_status: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    allegation_status: Mapped[str] = mapped_column(String(50), default="Reported", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    severity_score: Mapped[int] = mapped_column(Integer, default=1, index=True)
    dedupe_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    article = relationship("NewsArticle", back_populates="incident")
