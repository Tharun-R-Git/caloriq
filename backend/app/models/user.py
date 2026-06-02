from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    email = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)          # male / female / other
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String, default="moderate")
    aim = Column(String, nullable=True)             # lose / maintain / gain
    goal_calories = Column(Integer, default=2000)   # computed + cached on save
    dietary_preference = Column(String, nullable=True)   # veg / non_veg / eggetarian
    cuisine_preferences = Column(String, nullable=True)  # pipe-separated: north_indian|chinese
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
