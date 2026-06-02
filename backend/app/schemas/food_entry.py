import datetime
from typing import Optional
from pydantic import BaseModel


class FoodAnalyzeRequest(BaseModel):
    name: str
    description: Optional[str] = None


class FoodAnalyzeResponse(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    serving_size: str
    confidence: float


class FoodLogRequest(BaseModel):
    name: str
    description: Optional[str] = None
    calories: float
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    serving_size: Optional[str] = None
    date: Optional[datetime.date] = None


class FoodEntryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    serving_size: Optional[str] = None
    date: datetime.date
    logged_at: Optional[datetime.datetime] = None

    model_config = {"from_attributes": True}
