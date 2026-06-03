import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.dependencies import get_current_user
from app.models.food_entry import FoodEntry
from app.models.user import User
from app.schemas.food_entry import (
    FoodAnalyzeRequest, FoodAnalyzeResponse,
    FoodPhotoAnalyzeRequest, FoodPhotoAnalyzeResponse,
    FoodLogRequest, FoodEntryRead,
)
from app.services.gemini_service import GeminiService

router = APIRouter()


@router.post("/analyze", response_model=FoodAnalyzeResponse)
async def analyze_food(req: FoodAnalyzeRequest, user: User = Depends(get_current_user)):
    svc = GeminiService()
    return await svc.analyze_food(req.name, req.description)


@router.post("/analyze-photo", response_model=FoodPhotoAnalyzeResponse)
async def analyze_food_photo(req: FoodPhotoAnalyzeRequest, user: User = Depends(get_current_user)):
    svc = GeminiService()
    return await svc.analyze_food_photo(req.image_base64, req.mime_type)


@router.post("/log", response_model=FoodEntryRead, status_code=201)
async def log_food(
    req: FoodLogRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = FoodEntry(
        user_id=user.id,
        name=req.name,
        description=req.description,
        calories=req.calories,
        protein_g=req.protein_g,
        carbs_g=req.carbs_g,
        fat_g=req.fat_g,
        serving_size=req.serving_size,
        date=req.date or datetime.date.today(),
        logged_at=datetime.datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/today", response_model=list[FoodEntryRead])
async def get_today(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = datetime.date.today()
    result = await db.execute(
        select(FoodEntry)
        .where(FoodEntry.user_id == user.id, FoodEntry.date == today)
        .order_by(FoodEntry.logged_at.desc())
    )
    return result.scalars().all()


@router.get("/history")
async def get_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    since = datetime.date.today() - datetime.timedelta(days=29)
    result = await db.execute(
        select(FoodEntry)
        .where(FoodEntry.user_id == user.id, FoodEntry.date >= since)
        .order_by(FoodEntry.date.desc(), FoodEntry.logged_at.desc())
    )
    entries = result.scalars().all()

    grouped: dict[str, list] = {}
    for entry in entries:
        key = str(entry.date)
        grouped.setdefault(key, []).append(entry)

    return [
        {
            "date": date,
            "entries": [FoodEntryRead.model_validate(e) for e in day_entries],
            "total_calories": round(sum(e.calories for e in day_entries), 1),
        }
        for date, day_entries in grouped.items()
    ]


@router.get("", response_model=list[FoodEntryRead])
async def get_food_entries(
    date: datetime.date = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(FoodEntry).where(FoodEntry.user_id == user.id)
    if date:
        query = query.where(FoodEntry.date == date)
    result = await db.execute(query.order_by(FoodEntry.logged_at.desc()))
    return result.scalars().all()


@router.delete("/{entry_id}", status_code=204)
async def delete_food_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FoodEntry).where(FoodEntry.id == entry_id, FoodEntry.user_id == user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    await db.delete(entry)
    await db.commit()
