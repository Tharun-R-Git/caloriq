import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.models.food_entry import FoodEntry
from app.models.exercise_entry import ExerciseEntry
from app.routes.profile import get_or_create_user
from app.schemas.analytics import DailySummaryResponse
from app.services.analytics_service import get_daily_summary

router = APIRouter()


@router.get("/daily-summary", response_model=DailySummaryResponse)
async def daily_summary_full(db: AsyncSession = Depends(get_db)):
    return await get_daily_summary(db)


@router.get("/daily")
async def daily_summary(date: datetime.date = None, db: AsyncSession = Depends(get_db)):
    if not date:
        date = datetime.date.today()

    food_res = await db.execute(
        select(
            func.coalesce(func.sum(FoodEntry.calories), 0),
            func.coalesce(func.sum(FoodEntry.protein_g), 0),
            func.coalesce(func.sum(FoodEntry.carbs_g), 0),
            func.coalesce(func.sum(FoodEntry.fat_g), 0),
        ).where(FoodEntry.date == date)
    )
    cal, protein, carbs, fat = food_res.one()

    ex_res = await db.execute(
        select(func.coalesce(func.sum(ExerciseEntry.calories_burned), 0)).where(ExerciseEntry.date == date)
    )
    burned = ex_res.scalar()

    user = await get_or_create_user(db)

    return {
        "date": str(date),
        "calories_consumed": round(float(cal), 1),
        "calories_burned": round(float(burned), 1),
        "protein": round(float(protein), 1),
        "carbs": round(float(carbs), 1),
        "fat": round(float(fat), 1),
        "goal": user.goal_calories,
    }


@router.get("/weekly")
async def weekly_summary(db: AsyncSession = Depends(get_db)):
    # TODO: aggregate weekly averages and totals
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=6)
    return {"week_start": str(week_start), "week_end": str(today), "message": "TODO: implement weekly summary"}


@router.get("/trends")
async def trends(days: int = 30, db: AsyncSession = Depends(get_db)):
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days - 1)
    user = await get_or_create_user(db)

    results = []
    for i in range(days):
        d = start + datetime.timedelta(days=i)
        food_res = await db.execute(
            select(
                func.coalesce(func.sum(FoodEntry.calories), 0),
                func.coalesce(func.sum(FoodEntry.protein_g), 0),
                func.coalesce(func.sum(FoodEntry.carbs_g), 0),
                func.coalesce(func.sum(FoodEntry.fat_g), 0),
            ).where(FoodEntry.date == d)
        )
        cal, prot, carbs, fat = food_res.one()

        ex_res = await db.execute(
            select(func.coalesce(func.sum(ExerciseEntry.calories_burned), 0)).where(ExerciseEntry.date == d)
        )
        burned = ex_res.scalar()

        results.append({
            "date": str(d),
            "calories_consumed": round(float(cal), 1),
            "calories_burned": round(float(burned), 1),
            "protein": round(float(prot), 1),
            "carbs": round(float(carbs), 1),
            "fat": round(float(fat), 1),
            "goal": user.goal_calories,
        })

    return results
