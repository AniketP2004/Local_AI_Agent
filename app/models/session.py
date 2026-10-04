from sqlalchemy import Column, Text, String, Integer, DateTime
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, server_default=func.now())
    topic_filter = Column(String, nullable=True)
    difficulty_filter = Column(String, nullable=True)
    num_questions = Column(Integer, nullable=False)
    session_context = Column(Text, nullable=True)   # interview state JSON ONLY
    notes = Column(Text, nullable=True)             # teaching notes
    notes_topic = Column(String, nullable=True)     # topic the notes were written for
    mode = Column(String, nullable=False, default="practice", server_default="practice")