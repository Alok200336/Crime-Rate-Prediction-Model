from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import engine

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
