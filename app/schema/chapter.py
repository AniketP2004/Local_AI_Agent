
from pydantic import BaseModel, ConfigDict
from typing import List


class SubtopicOut(BaseModel):
    id: int
    name: str
    question_count: int

    model_config = ConfigDict(from_attributes=True)  # pydantic v2; use orm_mode=True if v1


class ChapterOut(BaseModel):
    id: int
    name: str
    subtopic_count: int
    question_count: int

    model_config = ConfigDict(from_attributes=True)


class ChapterDetailOut(BaseModel):
    id: int
    name: str
    subtopics: List[SubtopicOut]

    model_config = ConfigDict(from_attributes=True)


class SubtopicTopicsOut(BaseModel):
    id: int
    name: str
    topics: List[str]

class ChapterTopicsOut(BaseModel):
    id: int
    name: str
    subtopics: List[SubtopicTopicsOut]