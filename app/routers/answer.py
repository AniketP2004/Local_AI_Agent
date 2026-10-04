import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.attempt import Attempt
from app.models.question import Question
from app.models.session import Session as SessionModel
from app.schema.attempt import AnswerIn, VerdictOut, VoiceAnswerOut
from app.services.judge import grade_answer, LLMError
from app.services.stt import transcribe
from app.services import interview

router = APIRouter(prefix="/session", tags=["answer"])
log = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 10 * 1024 * 1024


def _process_answer(db: DBSession, session_id: str, question_id: str, answer_text: str):
    answer_text = (answer_text or "").strip()
    if not answer_text:
        raise HTTPException(400, "Empty answer")

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")

    attempt = (
        db.query(Attempt)
        .filter(Attempt.session_id == session_id, Attempt.question_id == question_id)
        .first()
    )
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    if attempt.user_answer is not None:
        raise HTTPException(409, "Already answered")

    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "Question not found")

    if session.mode == "interview":
        try:
            expected = interview.expected_question_id(session)
        except ValueError as e:
            raise HTTPException(409, str(e))
        if question_id != expected:
            raise HTTPException(409, "Not the current interview question")

    try:
        result = grade_answer(
            q.question, q.correct_answer, q.explanation, q.is_gotcha,
            answer_text, session_context=session.notes,
        )
    except LLMError as e:
        log.exception("grading failed")
        raise HTTPException(502, f"Grading failed, please retry: {e}")

    attempt.user_answer = answer_text
    attempt.verdict = result["verdict"]
    attempt.reasoning = result["reasoning"]

    try:
        if session.mode == "interview":
            interview.advance_after_answer(db, session, question_id, answer_text)
        db.commit()
    except Exception as e:
        db.rollback()  # attempt goes back to unanswered, user can retry
        log.exception("advance failed")
        raise HTTPException(502, f"Could not continue, please retry: {e}")

    return q, result, answer_text


@router.post("/{session_id}/answer", response_model=VerdictOut)
def submit_answer(session_id: str, body: AnswerIn, db: DBSession = Depends(get_db)):
    q, result, _ = _process_answer(db, session_id, body.question_id, body.answer_text)
    return VerdictOut(
        verdict=result["verdict"],
        reasoning=result["reasoning"],
        correct_answer=q.correct_answer,
        explanation=q.explanation,
    )


@router.post("/{session_id}/answer/voice", response_model=VoiceAnswerOut)
def submit_voice_answer(
    session_id: str,
    question_id: str,
    audio: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    audio_bytes = audio.file.read()
    if not audio_bytes:
        raise HTTPException(400, "Empty audio")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio too large")

    transcript = transcribe(audio_bytes)
    if not transcript:
        raise HTTPException(422, "No speech detected, please try again")

    q, result, transcript = _process_answer(db, session_id, question_id, transcript)
    return VoiceAnswerOut(
        transcript=transcript,
        verdict=result["verdict"],
        reasoning=result["reasoning"],
        correct_answer=q.correct_answer,
        explanation=q.explanation,
    )