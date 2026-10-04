from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.session import Session as SessionModel
from app.models.attempt import Attempt
from app.models.question import Question
from app.schema.session import SessionStart, SessionOut
from app.schema.question import QuestionOut
from app.services.sampler import sample_questions

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start", response_model=SessionOut)
def start_session(body: SessionStart, db: DBSession = Depends(get_db)):
    qs = sample_questions(db, body.topic, body.difficulty, body.num_questions)
    if not qs:
        raise HTTPException(404, "No questions match filter")

    new_session = SessionModel(
        topic_filter=body.topic,
        difficulty_filter=body.difficulty,
        num_questions=len(qs),
        mode="practice",
    )
    db.add(new_session)
    db.flush()

    for q in qs:
        db.add(Attempt(session_id=new_session.id, question_id=q.id))
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/{session_id}/next", response_model=QuestionOut)
def next_question(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.mode == "interview":
        raise HTTPException(400, "Use /interview/{id}/next for interview sessions")

    unanswered = (
        db.query(Attempt)
        .filter(
            Attempt.session_id == session_id,
            Attempt.user_answer.is_(None),
            Attempt.round.is_(None),          # practice attempts only, skip teach
        )
        .order_by(Attempt.id)
        .first()
    )
    if not unanswered:
        raise HTTPException(410, "Session complete")

    return db.query(Question).filter(Question.id == unanswered.question_id).first()