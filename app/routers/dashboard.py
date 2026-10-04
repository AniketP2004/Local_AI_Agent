from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.services.stats import topic_accuracy, weak_topics
from app.schema.dashboard import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(db: DBSession = Depends(get_db)):
    stats = topic_accuracy(db)
    weak = [t["topic"] for t in weak_topics(stats)]
    return DashboardOut(stats=stats, weak_topics=weak)