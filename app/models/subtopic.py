from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    order = Column(Integer, default=0)

    chapter = relationship("Chapter", back_populates="subtopics")
    questions = relationship("Question", back_populates="subtopic")