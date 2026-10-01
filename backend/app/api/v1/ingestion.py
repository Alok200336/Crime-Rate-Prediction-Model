from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.collectors.multi_source import MultiSourceCollector
from app.core.config import settings
from app.core.security import require_admin_key
from app.db.session import get_db
from app.pipelines.ingestion_pipeline import run_ingestion
from app.services.seed_data import seed_demo

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

@router.post("/run", dependencies=[Depends(require_admin_key)])
def trigger_ingestion(db: Session = Depends(get_db)):
    return run_ingestion(db, MultiSourceCollector())

@router.post("/seed-demo", dependencies=[Depends(require_admin_key)])
def seed(db: Session = Depends(get_db)):
    if not settings.demo_enabled: raise HTTPException(403, "Demo mode is disabled")
    return {"created": seed_demo(db)}
