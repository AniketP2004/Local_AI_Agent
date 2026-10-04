from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_attempt_session_question"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String, nullable=True)
    verdict = Column(String, nullable=True)
    answered_at = Column(DateTime, server_default=func.now())
    reasoning = Column(String, nullable=True)
    round = Column(String, nullable=True)   # None=practice, "conceptual"/"practical"=interview, "teach"