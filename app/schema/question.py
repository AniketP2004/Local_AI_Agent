from pydantic import BaseModel, ConfigDict


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    question: str
    topic: str
    difficulty: str
    is_gotcha: bool