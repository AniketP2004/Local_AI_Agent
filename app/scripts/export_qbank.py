"""Regenerate data/qbank.json from the DB (curated questions only).
Run from project root:  python -m app.scripts.export_qbank
"""
import json
from pathlib import Path
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.question import Question, bank_only

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "qbank.json"


def main():
    db = SessionLocal()
    try:
        rows = (
            bank_only(db.query(Question))
            .options(joinedload(Question.chapter), joinedload(Question.subtopic))
            .order_by(Question.topic, Question.id)
            .all()
        )
        data = [
            {
                "id": q.id,
                "question": q.question,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "is_gotcha": q.is_gotcha,
                "chapter": q.chapter.name if q.chapter else None,
                "subtopic": q.subtopic.name if q.subtopic else None,
            }
            for q in rows
        ]
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Exported {len(data)} questions to {OUT}")
    finally:
        db.close()


if __name__ == "__main__":
    main()