from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Crime Intelligence India API"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://crime:crime@db:5432/crime_intelligence"
    cors_origins: str = "http://localhost:8501,http://localhost:3000"
    news_rss_feeds: str = ""
    ingestion_interval_minutes: int = 60
    scheduler_enabled: bool = False
    redis_url: str = ""
    newsapi_key: str = ""
    demo_enabled: bool = False
    admin_api_key: str = "change-me"
    max_articles_per_feed: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @property
    def rss_feed_list(self) -> list[str]:
        return [x.strip() for x in self.news_rss_feeds.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
