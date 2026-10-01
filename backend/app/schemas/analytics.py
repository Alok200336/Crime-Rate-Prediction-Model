from pydantic import BaseModel


class CountItem(BaseModel):
    name: str
    count: int


class TrendItem(BaseModel):
    date: str
    count: int
