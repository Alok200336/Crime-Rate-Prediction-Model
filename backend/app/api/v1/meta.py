from fastapi import APIRouter, Depends
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.crime_incident import CrimeIncident

router = APIRouter(prefix="/meta", tags=["meta"])

@router.get("/filters")
def filters(db: Session = Depends(get_db)):
    crime_types = list(db.scalars(select(distinct(CrimeIncident.crime_type)).order_by(CrimeIncident.crime_type)).all())
    states = list(db.scalars(select(distinct(CrimeIncident.state)).where(CrimeIncident.state.is_not(None)).order_by(CrimeIncident.state)).all())
    return {"crime_types": crime_types, "states": states}
