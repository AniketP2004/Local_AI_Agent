from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.teach import (
    TeachNotesRequest, TeachNotesResponse, TeachQuizRequest, TeachQuizResponse,
)
from app.services.teach import generate_notes, generate_quiz_question
from app.services.judge import LLMError

router = APIRouter(prefix="/teach", tags=["teach"])


@router.post("/notes", response_model=TeachNotesResponse)
def get_notes(payload: TeachNotesRequest, db: Session = Depends(get_db)):
    try:
        notes = generate_notes(db, payload.session_id, payload.topic)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"Notes generation failed, please retry: {e}")
    return TeachNotesResponse(session_id=payload.session_id, notes=notes)


@router.post("/quiz", response_model=TeachQuizResponse)
def get_quiz_question(payload: TeachQuizRequest, db: Session = Depends(get_db)):
    try:
        return generate_quiz_question(db, payload.session_id, payload.topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"Quiz generation failed, please retry: {e}")