import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from app.db import Base


class ExerciseEntry(Base):
    __tablename__ = "exercise_entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration_minutes = Column(Float, default=0)
    intensity = Column(String, default="moderate")
    calories_burned = Column(Float, default=0)
    exercise_type = Column(String, default="cardio")
    date = Column(Date, default=datetime.date.today)
    logged_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
