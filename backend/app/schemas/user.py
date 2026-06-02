from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str = ""
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    goal_calories: int = 2000
    activity_level: str = "moderate"


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserRead(UserBase):
    id: int

    model_config = {"from_attributes": True}
