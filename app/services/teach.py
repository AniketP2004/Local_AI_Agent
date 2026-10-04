import uuid
from sqlalchemy.orm import Session as DBSession

from app.models.session import Session as SessionModel
from app.models.question import Question
from app.models.attempt import Attempt
from app.services.judge import call_nim, call_nim_json, LLMError

NOTES_PROMPT_TEMPLATE = """Write concise study notes on the topic below for
someone preparing for a Python interview. Cover the core concept, common
pitfalls, and one short code example. Keep it under 300 words.

Topic: {topic}
"""

QUIZ_FROM_NOTES_PROMPT = """Based only on the notes below, write ONE
interview question that tests understanding of this material. Do not
introduce concepts not covered in the notes.
{avoid_block}
Also give a correct reference answer and a short explanation.

Notes:
{notes}

Respond ONLY with JSON, no markdown fences:
{{"question": "...", "correct_answer": "...", "explanation": "..."}}
"""


def _get_teach_session(db: DBSession, session_id: str) -> SessionModel:
    session = db.query(SessionModel).filter_by(id=session_id).first()
    if not session:
        raise ValueError("Session not found")
    if session.mode == "interview":
        raise ValueError("Teaching is not available in an interview session")
    return session


def generate_notes(db: DBSession, session_id: str, topic: str) -> str:
    session = _get_teach_session(db, session_id)

    if not db.query(Question.id).filter(Question.topic == topic).first():
        raise ValueError(f"No questions found for topic '{topic}'")

    if session.notes and session.notes_topic == topic:
        return session.notes  # cached

    notes = call_nim(NOTES_PROMPT_TEMPLATE.format(topic=topic), temperature=0.3, max_tokens=1200)
    session.notes = notes.strip()
    session.notes_topic = topic
    db.commit()
    return session.notes


def generate_quiz_question(db: DBSession, session_id: str, topic: str) -> dict:
    session = _get_teach_session(db, session_id)
    if not session.notes:
        raise ValueError("No notes found for this session. Call /teach/notes first")

    previous = [
        text for (text,) in
        db.query(Question.question)
        .join(Attempt, Attempt.question_id == Question.id)
        .filter(Attempt.session_id == session_id, Question.source == "teach")
        .all()
    ]
    avoid_block = (
        "\nDo NOT repeat or rephrase any of these earlier questions:\n"
        + "\n".join(f"- {p}" for p in previous) + "\n"
    ) if previous else ""

    prompt = QUIZ_FROM_NOTES_PROMPT.format(avoid_block=avoid_block, notes=session.notes)
    parsed = call_nim_json(prompt, temperature=0.5)
    for key in ("question", "correct_answer", "explanation"):
        if not parsed.get(key):
            raise LLMError(f"Quiz JSON missing '{key}'")

    q = Question(
        id=str(uuid.uuid4()),
        question=str(parsed["question"]).strip(),
        correct_answer=str(parsed["correct_answer"]),
        explanation=str(parsed["explanation"]),
        topic=session.notes_topic or topic,
        difficulty="medium",
        is_gotcha=False,
        source="teach",
    )
    db.add(q)
    db.flush()
    db.add(Attempt(session_id=session_id, question_id=q.id, round="teach"))
    db.commit()
    return {"question_id": q.id, "question": q.question}