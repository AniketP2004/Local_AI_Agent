from pydantic import BaseModel, Field
from typing import Literal

Verdict = Literal["correct", "partial", "wrong"]


class AnswerIn(BaseModel):
    question_id: str
    answer_text: str = Field(min_length=1)


class VerdictOut(BaseModel):
    verdict: Verdict
    reasoning: str
    correct_answer: str
    explanation: str


class VoiceAnswerOut(BaseModel):
    transcript: str
    verdict: Verdict
    reasoning: str
    correct_answer: str
    explanation: str