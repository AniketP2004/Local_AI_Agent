from pydantic import BaseModel, Field
from typing import Literal, Optional


class InterviewStartIn(BaseModel):
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    num_questions: int = Field(5, ge=1, le=30)


class InterviewStartOut(BaseModel):
    session_id: str
    num_questions: int


class InterviewNextOut(BaseModel):
    round: Literal["conceptual", "practical", "done"]
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    is_final: bool = False