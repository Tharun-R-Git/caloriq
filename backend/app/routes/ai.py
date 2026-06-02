from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationService

router = APIRouter()


class MealAnalysisRequest(BaseModel):
    description: str


@router.get("/suggestions")
async def get_suggestions(db: AsyncSession = Depends(get_db)):
    # TODO: gather recent food/exercise context before generating suggestions
    service = RecommendationService()
    return await service.get_suggestions(db)


@router.post("/analyze-meal")
async def analyze_meal(request: MealAnalysisRequest):
    # TODO: wire result back to food logger so user can confirm and save
    service = GeminiService()
    return await service.analyze_meal(request.description)
