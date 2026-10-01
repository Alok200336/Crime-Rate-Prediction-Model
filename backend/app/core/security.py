import secrets
from fastapi import Header, HTTPException
from app.core.config import settings

def require_admin_key(x_admin_key: str | None = Header(default=None)):
    if not settings.admin_api_key or settings.admin_api_key == "change-me":
        raise HTTPException(503, "Set a non-default ADMIN_API_KEY to enable administration")
    if not x_admin_key or not secrets.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(401, "Invalid admin API key")
