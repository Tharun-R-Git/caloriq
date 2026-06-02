from dotenv import load_dotenv
load_dotenv()  # no-op if .env is absent (production)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routes import food, exercise, profile, analytics, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="CaloriQ API", version="0.1.0", lifespan=lifespan)

import os
_EXTRA_ORIGIN = os.getenv("FRONTEND_URL", "")
_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]
if _EXTRA_ORIGIN:
    _ORIGINS.append(_EXTRA_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(food.router, prefix="/api/food", tags=["food"])
app.include_router(exercise.router, prefix="/api/exercise", tags=["exercise"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}
