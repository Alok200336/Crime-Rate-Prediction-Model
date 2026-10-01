from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.tasks.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(); init_db(); start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title=settings.app_name, version="2.0.0", description="News-derived crime intelligence API for India.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.get("/")
def root():
    return {"message": settings.app_name, "docs": "/docs"}
