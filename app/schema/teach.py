from pydantic import BaseModel


class TeachNotesRequest(BaseModel):
    topic: str
    session_id: str


class TeachNotesResponse(BaseModel):
    session_id: str
    notes: str


class TeachQuizRequest(BaseModel):
    session_id: str
    topic: str


class TeachQuizResponse(BaseModel):
    question_id: str
    question: str