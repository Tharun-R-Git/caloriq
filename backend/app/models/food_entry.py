import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from app.db import Base


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    calories = Column(Float, default=0)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    serving_size = Column(String, nullable=True)
    date = Column(Date, default=datetime.date.today)
    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
