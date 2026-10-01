from urllib.parse import urlparse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.news_article import NewsArticle
from app.schemas.news import NewsArticleCreate


def get_by_url(db: Session, url: str) -> NewsArticle | None:
    return db.scalar(select(NewsArticle).where(NewsArticle.url == url))


def create(db: Session, payload: NewsArticleCreate) -> NewsArticle:
    url = str(payload.url)
    article = NewsArticle(
        title=payload.title, summary=payload.summary, raw_text=payload.raw_text,
        source_name=payload.source_name, source_domain=urlparse(url).netloc,
        url=url, published_at=payload.published_at,
    )
    db.add(article); db.commit(); db.refresh(article)
    return article
