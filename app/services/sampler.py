from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from app.models.question import Question, bank_only


def sample_questions(db: DBSession, topic: str | None, difficulty: str | None, n: int):
    q = bank_only(db.query(Question))
    if topic:
        q = q.filter(Question.topic == topic)
    if difficulty:
        q = q.filter(Question.difficulty == difficulty)
    return q.order_by(func.random()).limit(n).all()