from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl


class NewsArticleCreate(BaseModel):
    title: str
    summary: str | None = None
    raw_text: str | None = None
    source_name: str | None = None
    url: HttpUrl
    published_at: datetime | None = None


class NewsArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    summary: str | None
    source_name: str | None
    source_domain: str | None
    url: str
    published_at: datetime | None
    fetched_at: datetime
    processed: bool
