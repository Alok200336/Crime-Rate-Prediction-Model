from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories import crime_repository
from app.schemas.crime import CrimeIncidentRead
from app.utils.serializers import incident_to_dict

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("/latest", response_model=list[CrimeIncidentRead])
def latest_incidents(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return [incident_to_dict(x) for x in crime_repository.latest(db, limit)]

@router.get("/search", response_model=list[CrimeIncidentRead])
def search_incidents(q: str | None = None, crime_type: str | None = None, state: str | None = None, limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    return [incident_to_dict(x) for x in crime_repository.search(db, q, crime_type, state, limit)]
