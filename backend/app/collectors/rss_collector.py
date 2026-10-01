from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import html, re
import feedparser, httpx
from app.collectors.base import NewsCollector
from app.core.config import settings
from app.schemas.news import NewsArticleCreate
from app.services.deduplication import canonical_url

TAG_RE = re.compile(r"<[^>]+>")
def clean_html(value): return html.unescape(TAG_RE.sub(" ", value)).strip()

class RSSCollector(NewsCollector):
    def __init__(self, feed_urls):
        self.feed_urls = feed_urls
        self.errors = []
    def fetch(self):
        self.errors = []
        articles = []
        with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "CrimeIntelligenceResearch/2.0"}) as client:
            for url in self.feed_urls:
                try:
                    with client.stream("GET", url) as response:
                        response.raise_for_status()
                        body = bytearray()
                        for chunk in response.iter_bytes():
                            body.extend(chunk)
                            if len(body) > 5_000_000: raise ValueError("Feed too large")
                    feed = feedparser.parse(bytes(body))
                    if not feed.entries and feed.bozo: raise ValueError("Invalid RSS/Atom")
                    for entry in feed.entries[:settings.max_articles_per_feed]:
                        try:
                            articles.append(NewsArticleCreate(title=clean_html(entry.get("title", ""))[:500], summary=clean_html(entry.get("summary", ""))[:1200] or None, url=canonical_url(entry.get("link", "")), source_name=feed.feed.get("title", "RSS")[:255], published_at=self._parse_date(entry.get("published") or entry.get("updated"))))
                        except (ValueError, TypeError):
                            self.errors.append("Skipped invalid RSS entry")
                except Exception as exc:
                    self.errors.append(f"Feed {self.feed_urls.index(url)+1}: {type(exc).__name__}")
        return articles
    @staticmethod
    def _parse_date(value):
        if not value: return None
        try: dt = parsedate_to_datetime(value)
        except (ValueError, TypeError):
            try: dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except (ValueError, TypeError): return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
