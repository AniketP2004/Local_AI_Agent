# --- New file: app/routers/interview.py ---

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.schema.interview import InterviewStartIn, InterviewStartOut, InterviewNextOut
from app.services import interview

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/start", response_model=InterviewStartOut)
def start(payload: InterviewStartIn, db: DBSession = Depends(get_db)):
    try:
        result = interview.start_interview(db, payload.topic, payload.difficulty, payload.num_questions)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{session_id}/next", response_model=InterviewNextOut)
def next_question(session_id: str, db: DBSession = Depends(get_db)):
    try:
        result = interview.get_next_question(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result