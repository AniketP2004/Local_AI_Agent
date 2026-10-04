from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    topic = Column(String, nullable=False, index=True)
    difficulty = Column(String, nullable=False)
    is_gotcha = Column(Boolean, default=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    parent_question_id = Column(String, ForeignKey("questions.id"), nullable=True)
    source = Column(String, nullable=True)  # NULL = curated bank, "practical" | "teach" = generated

    chapter = relationship("Chapter")
    subtopic = relationship("Subtopic", back_populates="questions")


def bank_only(query):
    """Restrict a query to curated bank questions (no generated rows)."""
    return query.filter(Question.parent_question_id.is_(None), Question.source.is_(None))