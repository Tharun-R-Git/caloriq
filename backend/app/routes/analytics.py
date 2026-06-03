import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import DailySummaryResponse, DailyResponse, TrendDay
from app.services.analytics_service import get_daily_summary, get_daily_for_date, get_trends

router = APIRouter()


@router.get("/daily-summary", response_model=DailySummaryResponse)
async def daily_summary_full(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_daily_summary(db, user)


@router.get("/daily", response_model=DailyResponse)
async def daily_summary(
    date: datetime.date = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_daily_for_date(db, date or datetime.date.today(), user)


@router.get("/weekly")
async def weekly_summary(user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Weekly summary not yet implemented")


@router.get("/trends", response_model=list[TrendDay])
async def trends(
    days: int = 14,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_trends(db, days, user)
