"""Seed DB from data/qbank.json.  Run:  python -m app.scripts.seed_qbank"""
import json
from pathlib import Path

from app.database import SessionLocal, Base, engine
from app import models  # noqa: F401
from app.models.chapter import Chapter
from app.models.subtopic import Subtopic
from app.models.question import Question

ROOT = Path(__file__).resolve().parents[2]
QBANK_FILE = ROOT / "data" / "qbank.json"

COLUMNS = {
    "id", "question", "correct_answer", "explanation", "topic", "difficulty",
    "is_gotcha", "chapter_id", "subtopic_id",
}


def seed():
    Base.metadata.create_all(bind=engine)
    data = json.loads(QBANK_FILE.read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        existing = {i for (i,) in db.query(Question.id).all()}
        chapters, subtopics = {}, {}
        added = 0

        for q in data:
            if "id" not in q or q["id"] in existing:
                continue
            fields = {k: v for k, v in q.items() if k in COLUMNS}

            ch_name, st_name = q.get("chapter"), q.get("subtopic")
            if ch_name:
                ch = chapters.get(ch_name) or db.query(Chapter).filter_by(name=ch_name).first()
                if not ch:
                    ch = Chapter(name=ch_name, order=len(chapters))
                    db.add(ch)
                    db.flush()
                chapters[ch_name] = ch
                fields["chapter_id"] = ch.id
                if st_name:
                    key = (ch.id, st_name)
                    st = subtopics.get(key) or db.query(Subtopic).filter_by(
                        name=st_name, chapter_id=ch.id).first()
                    if not st:
                        st = Subtopic(name=st_name, chapter_id=ch.id)
                        db.add(st)
                        db.flush()
                    subtopics[key] = st
                    fields["subtopic_id"] = st.id

            db.add(Question(**fields))
            added += 1

        db.commit()
        print(f"Seeded {added} new questions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()