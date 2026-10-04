from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class SessionStart(BaseModel):
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    num_questions: int = Field(5, ge=1, le=50)


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    num_questions: int