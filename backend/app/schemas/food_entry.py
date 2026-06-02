import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


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


class FoodPhotoAnalyzeRequest(BaseModel):
    image_base64: str
    mime_type: str

    @field_validator("mime_type")
    @classmethod
    def must_be_image(cls, v: str) -> str:
        if v not in ("image/jpeg", "image/png"):
            raise ValueError("mime_type must be image/jpeg or image/png")
        return v

    @field_validator("image_base64")
    @classmethod
    def limit_size(cls, v: str) -> str:
        # ~10 MB decoded ≈ ~13.6 MB base64
        if len(v) > 14_000_000:
            raise ValueError("Image too large (max ~10 MB)")
        return v


class FoodPhotoAnalyzeResponse(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    food_name: str
    serving_size: str
    confidence: float
    items_detected: list[str]
    not_available: bool = False


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
