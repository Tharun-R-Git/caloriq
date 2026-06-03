from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationService

router = APIRouter()

_rec_service = RecommendationService()


class MealAnalysisRequest(BaseModel):
    description: str = Field(..., min_length=2, max_length=500)


class MealRecommendationItem(BaseModel):
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    reason: str
    portion_size: str


class ExerciseSuggestionItem(BaseModel):
    name: str
    duration_minutes: int
    calories_burned: int
    reason: str


class RecommendationsResponse(BaseModel):
    recommendations: list[MealRecommendationItem]
    exercise_suggestions: list[ExerciseSuggestionItem] = []
    remaining_calories: int
    over_goal: bool = False
    message: str


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    meal_source: str = "home",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _rec_service.get_meal_recommendations(db, user, meal_source=meal_source)


@router.get("/suggestions")
async def get_suggestions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _rec_service.get_suggestions(db, user)


@router.post("/analyze-meal")
async def analyze_meal(request: MealAnalysisRequest, user: User = Depends(get_current_user)):
    try:
        service = GeminiService()
        return await service.analyze_food(request.description)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI analysis unavailable") from exc
