"""
One-time seed: reads generated_questions_review.json, extracts every
unique (chapter, subtopic) pair, and inserts Chapter/Subtopic rows using
those EXACT names — so merge_questions.py's name lookup succeeds.

Usage: python -m app.scripts.seed_chapters_from_review
"""

import json
from pathlib import Path
from sqlalchemy import func
from app.database import SessionLocal
from app.models.chapter import Chapter
from app.models.subtopic import Subtopic

REVIEW_FILE = Path(__file__).resolve().parents[2] / "generated_questions_review.json"


def main():
    data = json.loads(REVIEW_FILE.read_text(encoding="utf-8"))

    pairs = list(dict.fromkeys((q["chapter"], q["subtopic"]) for q in data)) 

    db = SessionLocal()
    try:
        chapter_cache = {}
        created_chapters = 0
        created_subtopics = 0

        next_order = (db.query(func.max(Chapter.order)).scalar() or 0) + 1

        for chapter_name, subtopic_name in pairs:
            if chapter_name not in chapter_cache:
                chapter = db.query(Chapter).filter_by(name=chapter_name).first()
                if not chapter:
                    chapter = Chapter(name=chapter_name, order=next_order + created_chapters) 
                    db.add(chapter)
                    db.flush()
                    created_chapters += 1
                chapter_cache[chapter_name] = chapter
            chapter = chapter_cache[chapter_name]

            existing_subtopic = db.query(Subtopic).filter_by(
                name=subtopic_name, chapter_id=chapter.id
            ).first()
            if not existing_subtopic:
                db.add(Subtopic(name=subtopic_name, chapter_id=chapter.id))
                created_subtopics += 1

        db.commit()
        print(f"Created {created_chapters} chapters, {created_subtopics} subtopics.")
        print(f"Total unique pairs processed: {len(pairs)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()