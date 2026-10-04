"""Merge reviewed questions into DB and data/qbank.json.
Run from project root:  python -m app.scripts.merge_questions
"""
import json
import shutil
import uuid
from pathlib import Path

from app.database import SessionLocal
from app.models.chapter import Chapter
from app.models.subtopic import Subtopic
from app.models.question import Question

ROOT = Path(__file__).resolve().parents[2]
REVIEW_FILE = ROOT / "generated_questions_review.json"
QBANK_FILE = ROOT / "data" / "qbank.json"


def read_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    reviewed = read_json(REVIEW_FILE, [])
    shutil.copy(REVIEW_FILE, REVIEW_FILE.with_suffix(".json.bak"))

    db = SessionLocal()
    remaining = []          # everything NOT merged stays in the review file
    merged = dup = not_found = 0

    try:
        qbank = read_json(QBANK_FILE, [])
        seen = {t for (t,) in db.query(Question.question).all()} | {r["question"] for r in qbank}
        new_rows = []

        for q in reviewed:
            if q.get("reviewed") is not True:
                remaining.append(q)
                continue

            if q["question"] in seen:
                dup += 1                      # already in DB or qbank, drop from review
                continue

            chapter = db.query(Chapter).filter_by(name=q["chapter"]).first()
            subtopic = (
                db.query(Subtopic).filter_by(name=q["subtopic"], chapter_id=chapter.id).first()
                if chapter else None
            )
            if not chapter or not subtopic:
                print(f"Not found ({q['chapter']} / {q['subtopic']}): {q['question'][:50]}...")
                remaining.append(q)           # keep for next run
                not_found += 1
                continue

            qid = str(uuid.uuid4())
            explanation = q.get("gotcha_explanation") or q["expected_answer"]
            difficulty = q.get("difficulty") or ("hard" if q["is_gotcha"] else "medium")

            db.add(Question(
                id=qid, question=q["question"], correct_answer=q["expected_answer"],
                explanation=explanation, topic=q["subtopic"], difficulty=difficulty,
                is_gotcha=q["is_gotcha"], chapter_id=chapter.id, subtopic_id=subtopic.id,
            ))
            new_rows.append({
                "id": qid, "question": q["question"], "correct_answer": q["expected_answer"],
                "explanation": explanation, "topic": q["subtopic"], "difficulty": difficulty,
                "is_gotcha": q["is_gotcha"], "chapter": q["chapter"], "subtopic": q["subtopic"],
            })
            seen.add(q["question"])
            merged += 1

        db.commit()
        write_json(QBANK_FILE, qbank + new_rows)
        write_json(REVIEW_FILE, remaining)     # only unmerged items remain

        print(f"Merged: {merged} | Duplicates dropped: {dup} | "
              f"Not found (kept): {not_found} | Unreviewed (kept): {len(remaining) - not_found}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()