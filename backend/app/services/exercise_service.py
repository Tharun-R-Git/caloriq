import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.exercise_entry import ExerciseEntry
from app.models.user import User
from app.schemas.exercise_entry import ExerciseLogRequest
from app.services.calorie_engine import CalorieEngine

_engine = CalorieEngine()
DEFAULT_WEIGHT_KG = 70.0


async def get_weight(db: AsyncSession) -> float:
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user and user.weight_kg:
        return user.weight_kg
    return DEFAULT_WEIGHT_KG


async def log_exercise(db: AsyncSession, req: ExerciseLogRequest) -> ExerciseEntry:
    weight_kg = await get_weight(db)
    if req.calories_burned_override is not None:
        calories = req.calories_burned_override
    else:
        calories = _engine.calculate_exercise_calories(
            req.name, req.intensity, req.duration_minutes, weight_kg
        )
    entry = ExerciseEntry(
        name=req.name,
        duration_minutes=req.duration_minutes,
        intensity=req.intensity,
        calories_burned=calories,
        date=req.date or datetime.date.today(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_today(db: AsyncSession) -> dict:
    today = datetime.date.today()
    result = await db.execute(
        select(ExerciseEntry)
        .where(ExerciseEntry.date == today)
        .order_by(ExerciseEntry.id.desc())
    )
    entries = result.scalars().all()
    return {
        "entries": entries,
        "total_burned": round(sum(e.calories_burned for e in entries), 1),
    }


async def get_entries(db: AsyncSession, date: datetime.date | None) -> list[ExerciseEntry]:
    query = select(ExerciseEntry)
    if date:
        query = query.where(ExerciseEntry.date == date)
    result = await db.execute(query.order_by(ExerciseEntry.id.desc()))
    return result.scalars().all()


async def delete_entry(db: AsyncSession, entry_id: int) -> None:
    """Raises ValueError if the entry does not exist."""
    result = await db.execute(select(ExerciseEntry).where(ExerciseEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise ValueError(f"Exercise entry {entry_id} not found")
    await db.delete(entry)
    await db.commit()
