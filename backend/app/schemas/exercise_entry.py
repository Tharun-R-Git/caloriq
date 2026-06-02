import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ExerciseEntryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    duration_minutes: float = Field(0, ge=0)
    calories_burned: float = Field(0, ge=0)
    exercise_type: Literal["cardio", "strength", "flexibility", "sports", "other"] = "cardio"
    date: datetime.date


class ExerciseEntryCreate(ExerciseEntryBase):
    pass


class ExerciseEntryRead(ExerciseEntryBase):
    id: int
    intensity: Optional[str] = "moderate"

    model_config = {"from_attributes": True}


# --- schemas for /log and /today routes ---

class ExerciseLogRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    duration_minutes: float = Field(..., gt=0)
    intensity: str = Field("moderate", pattern="^(light|moderate|vigorous)$")
    date: Optional[datetime.date] = None


class ExerciseLogResponse(BaseModel):
    id: int
    name: str
    duration_minutes: float
    intensity: str
    calories_burned: float
    date: datetime.date

    model_config = {"from_attributes": True}


class TodayExerciseResponse(BaseModel):
    entries: list[ExerciseLogResponse]
    total_burned: float
