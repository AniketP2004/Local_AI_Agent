from dotenv import load_dotenv
load_dotenv()

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401  registers all tables on Base.metadata
from app.routers import session as session_router, answer as answer_router
from app.routers import dashboard as dashboard_router
from app.routers import teach, interview
from app.routers import chapters
from app.services.stt import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if os.getenv("PRELOAD_WHISPER", "1") == "1":
        get_model()  # avoid slow first voice request
    yield


app = FastAPI(lifespan=lifespan)

# .env: ALLOWED_ORIGINS=http://localhost:5500,https://your-frontend.example
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router.router)
app.include_router(answer_router.router)
app.include_router(dashboard_router.router)
app.include_router(teach.router)
app.include_router(interview.router)
app.include_router(chapters.router)
# Register chapters only after M-8 (FK backfill) is done:
# from app.routers import chapters
