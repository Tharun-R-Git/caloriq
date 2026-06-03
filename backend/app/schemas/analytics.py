import datetime
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
    protein_goal_g: int
    carbs_goal_g: int
    fat_goal_g: int
    recent_foods: list[RecentFood]


class DailyResponse(BaseModel):
    date: datetime.date
    calories_in: float
    calories_burned: float
    protein_g: float
    carbs_g: float
    fat_g: float
    goal: int


class TrendDay(BaseModel):
    date: datetime.date
    calories_in: float
    calories_burned: float
    net: float
    protein_g: float
    carbs_g: float
    fat_g: float
    goal: int
