
from app.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    order = Column(Integer, default=0)

    subtopics = relationship("Subtopic", back_populates="chapter", cascade="all, delete-orphan")