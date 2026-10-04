from pydantic import BaseModel
from typing import List

class TopicStat(BaseModel):
    topic: str
    total: int
    correct: int
    accuracy: float

class DashboardOut(BaseModel):
    stats: List[TopicStat]
    weak_topics: List[str]