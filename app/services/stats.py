from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func, case
from app.models.attempt import Attempt
from app.models.question import Question


def topic_accuracy(db: DBSession):
    rows = (
        db.query(
            Question.topic,
            func.count(Attempt.id).label("total"),
            func.coalesce(func.sum(case((Attempt.verdict == "correct", 1), else_=0)), 0).label("correct"),
        )
        .join(Attempt, Attempt.question_id == Question.id)
        .filter(Attempt.verdict.isnot(None))
        .group_by(Question.topic)
        .all()
    )
    return [
        {
            "topic": r.topic,
            "total": r.total,
            "correct": int(r.correct),
            "accuracy": round(int(r.correct) / r.total * 100, 1) if r.total else 0.0,
        }
        for r in rows
    ]


def weak_topics(stats: list[dict], threshold: float = 60.0, min_attempts: int = 3):
    return [t for t in stats if t["total"] >= min_attempts and t["accuracy"] < threshold]