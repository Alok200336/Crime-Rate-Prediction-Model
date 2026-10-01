from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.crime_incident import CrimeIncident
from app.repositories import crime_repository
from app.schemas.analytics import CountItem, TrendItem
from app.schemas.crime import DashboardStats

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    total, today, states, sources, top = crime_repository.dashboard_stats(db)
    return DashboardStats(total_incidents=total, incidents_today=today, states_covered=states, sources_covered=sources, top_crime_type=top)

@router.get("/crime-types", response_model=list[CountItem])
def crime_types(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return [CountItem(name=n, count=c) for n,c in crime_repository.counts_by_field(db, CrimeIncident.crime_type, days)]

@router.get("/states", response_model=list[CountItem])
def states(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return [CountItem(name=n, count=c) for n,c in crime_repository.counts_by_field(db, CrimeIncident.state, days)]

@router.get("/trend", response_model=list[TrendItem])
def trend(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return [TrendItem(date=d, count=c) for d,c in crime_repository.daily_trend(db, days)]

@router.get("/trending", response_model=list[CountItem])
def trending(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    return [CountItem(name=n, count=c) for n,c in crime_repository.counts_by_field(db, CrimeIncident.crime_type, days, 10)]
