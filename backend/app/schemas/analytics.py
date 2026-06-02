from pydantic import BaseModel


class RecentFood(BaseModel):
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class DailySummaryResponse(BaseModel):
    calories_in: int
    calories_burned: int
    net_calories: int
    daily_goal: int
    remaining: int
    protein_g: float
    carbs_g: float
    fat_g: float
    recent_foods: list[RecentFood]
