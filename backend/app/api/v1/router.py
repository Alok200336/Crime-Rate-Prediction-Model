from fastapi import APIRouter
from app.api.v1 import analytics, health, incidents, ingestion, meta

api_router = APIRouter()
for router in (health.router, incidents.router, analytics.router, ingestion.router, meta.router):
    api_router.include_router(router)

from app.api.v1.intelligence import router as intelligence_router
api_router.include_router(intelligence_router)
