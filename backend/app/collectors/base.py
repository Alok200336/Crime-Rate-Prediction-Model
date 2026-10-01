from abc import ABC, abstractmethod
from app.schemas.news import NewsArticleCreate


class NewsCollector(ABC):
    @abstractmethod
    def fetch(self) -> list[NewsArticleCreate]:
        raise NotImplementedError
