from typing import Optional
from pydantic import BaseModel, field_validator
from typing import Literal


class ProfileSetup(BaseModel):
    name: str
    email: Optional[str] = None
    age: int
    gender: Literal["male", "female", "other"]
    height_cm: float
    weight_kg: float
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    aim: Literal["lose", "maintain", "gain"]
    dietary_preference: Optional[Literal["veg", "non_veg", "eggetarian"]] = None
    cuisine_preferences: Optional[list[str]] = None

    @field_validator("age")
    @classmethod
    def age_range(cls, v):
        if not (10 <= v <= 100):
            raise ValueError("age must be between 10 and 100")
        return v

    @field_validator("height_cm")
    @classmethod
    def height_range(cls, v):
        if not (100 <= v <= 250):
            raise ValueError("height_cm must be between 100 and 250")
        return v

    @field_validator("weight_kg")
    @classmethod
    def weight_range(cls, v):
        if not (20 <= v <= 300):
            raise ValueError("weight_kg must be between 20 and 300")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal["male", "female", "other"]] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very_active"]] = None
    aim: Optional[Literal["lose", "maintain", "gain"]] = None
    goal_calories: Optional[int] = None
    dietary_preference: Optional[Literal["veg", "non_veg", "eggetarian"]] = None
    cuisine_preferences: Optional[list[str]] = None


class GoalsResponse(BaseModel):
    bmr: float
    tdee: float
    daily_goal: int
    protein_goal_g: float
    carbs_goal_g: float
    fat_goal_g: float


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: str
    aim: Optional[str] = None
    goal_calories: int
    is_setup: bool
    goals: Optional[GoalsResponse] = None
    dietary_preference: Optional[str] = None
    cuisine_preferences: Optional[list[str]] = None


# Kept for backward compatibility with analytics schemas
class UserBase(BaseModel):
    name: str = ""
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    goal_calories: int = 2000
    activity_level: str = "moderate"


class UserRead(UserBase):
    id: int
    model_config = {"from_attributes": True}
