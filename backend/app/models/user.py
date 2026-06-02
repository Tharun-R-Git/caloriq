from sqlalchemy import Column, Integer, String, Float
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    age = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    goal_calories = Column(Integer, default=2000)
    activity_level = Column(String, default="moderate")
