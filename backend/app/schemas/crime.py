from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class CrimeIncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    article_id: int
    crime_type: str
    crime_subtype: str | None
    title: str
    summary: str | None
    incident_date: date | None
    state: str | None
    district: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    victim_count: int | None
    suspect_count: int | None
    case_status: str | None
    allegation_status: str
    confidence_score: float
    severity_score: int
    created_at: datetime
    source_name: str | None = None
    article_url: str | None = None
    published_at: datetime | None = None


class DashboardStats(BaseModel):
    total_incidents: int
    incidents_today: int
    states_covered: int
    sources_covered: int
    top_crime_type: str | None
