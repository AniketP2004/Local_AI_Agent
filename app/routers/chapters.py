from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.chapter import Chapter
from app.models.subtopic import Subtopic
from app.models.question import Question, bank_only
from app.schema.chapter import ChapterOut, SubtopicOut, ChapterDetailOut, SubtopicTopicsOut, ChapterTopicsOut

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("", response_model=list[ChapterOut])
def list_chapters(db: Session = Depends(get_db)):
    chapters = db.query(Chapter).order_by(Chapter.order).all()
    sub_counts = dict(
        db.query(Subtopic.chapter_id, func.count(Subtopic.id))
        .group_by(Subtopic.chapter_id).all()
    )
    q_counts = dict(
        bank_only(db.query(Question.chapter_id, func.count(Question.id)))
        .group_by(Question.chapter_id).all()
    )
    return [
        ChapterOut(
            id=c.id, name=c.name,
            subtopic_count=sub_counts.get(c.id, 0),
            question_count=q_counts.get(c.id, 0),
        )
        for c in chapters
    ]


@router.get("/{chapter_id}/subtopics", response_model=ChapterDetailOut)
def get_chapter_subtopics(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    counts = dict(
        bank_only(db.query(Question.subtopic_id, func.count(Question.id)))
        .filter(Question.chapter_id == chapter_id)
        .group_by(Question.subtopic_id).all()
    )
    return ChapterDetailOut(
        id=chapter.id,
        name=chapter.name,
        subtopics=[
            SubtopicOut(id=s.id, name=s.name, question_count=counts.get(s.id, 0))
            for s in chapter.subtopics
        ],
    )

@router.get("/topics", response_model=list[ChapterTopicsOut])
def list_topics_grouped(db: Session = Depends(get_db)):
    chapters = db.query(Chapter).order_by(Chapter.order).all()
    result = []
    for ch in chapters:
        subtopics_out = []
        for st in sorted(ch.subtopics, key=lambda s: s.order):
            topics = [
                t for (t,) in
                bank_only(db.query(Question.topic))
                .filter(Question.subtopic_id == st.id)
                .distinct().order_by(Question.topic).all()
            ]
            if topics:
                subtopics_out.append(SubtopicTopicsOut(id=st.id, name=st.name, topics=topics))
        if subtopics_out:
            result.append(ChapterTopicsOut(id=ch.id, name=ch.name, subtopics=subtopics_out))
    return result