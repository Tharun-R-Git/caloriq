import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.exercise_entry import (
    ExerciseEntryRead,
    ExerciseAnalyzeRequest, ExerciseAnalyzeResponse,
    ExerciseLogRequest, ExerciseLogResponse, TodayExerciseResponse,
)
from app.services.gemini_service import GeminiService
import app.services.exercise_service as svc

router = APIRouter()


@router.post("/analyze", response_model=ExerciseAnalyzeResponse)
async def analyze_exercise(
    req: ExerciseAnalyzeRequest,
    user: User = Depends(get_current_user),
):
    try:
        weight_kg = svc.get_weight(user)
        ai = GeminiService()
        return await ai.analyze_exercise(req.description, req.duration_minutes, weight_kg)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/log", response_model=ExerciseLogResponse, status_code=201)
async def log_exercise(
    req: ExerciseLogRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await svc.log_exercise(db, req, user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/today", response_model=TodayExerciseResponse)
async def get_today_exercise(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await svc.get_today(db, user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{entry_id}", status_code=204)
async def delete_exercise_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await svc.delete_entry(db, entry_id, user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# Legacy route — GET with optional date filter
@router.get("", response_model=list[ExerciseEntryRead])
async def get_exercise_entries(
    date: datetime.date = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await svc.get_entries(db, date, user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# Legacy POST — routes through MET calculation so calories are always computed
@router.post("", response_model=ExerciseLogResponse, status_code=201)
async def create_exercise_entry(
    req: ExerciseLogRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await svc.log_exercise(db, req, user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
