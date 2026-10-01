import httpx
from app.collectors.rss_collector import RSSCollector
from app.core.config import settings
from app.schemas.news import NewsArticleCreate
from app.services.deduplication import canonical_url

class MultiSourceCollector:
    def __init__(self): self.errors = []
    def fetch(self):
        rss = RSSCollector(settings.rss_feed_list)
        items = rss.fetch(); self.errors = list(rss.errors)
        if settings.newsapi_key:
            try:
                response = httpx.get("https://newsapi.org/v2/everything", params={"q": "India AND (crime OR police OR robbery OR fraud)", "language": "en", "sortBy": "publishedAt", "pageSize": 100}, headers={"X-Api-Key": settings.newsapi_key}, timeout=25)
                response.raise_for_status()
                data = response.json()
                if data.get("status") != "ok": raise ValueError("Provider error")
                for a in data.get("articles", []):
                    try:
                        items.append(NewsArticleCreate(title=(a.get("title") or "")[:500], summary=(a.get("description") or "")[:1200], url=canonical_url(a["url"]), source_name=a.get("source", {}).get("name"), published_at=RSSCollector._parse_date(a.get("publishedAt"))))
                    except (ValueError, KeyError, TypeError): self.errors.append("Skipped invalid NewsAPI entry")
            except Exception as exc: self.errors.append(f"NewsAPI: {type(exc).__name__}")
        if not settings.rss_feed_list and not settings.newsapi_key:
            self.errors.append("No sources configured; set NEWS_RSS_FEEDS or NEWSAPI_KEY")
        return items
