import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.exercise_entry import ExerciseEntry
from app.models.user import User
from app.schemas.exercise_entry import ExerciseLogRequest
from app.services.calorie_engine import CalorieEngine

_engine = CalorieEngine()
DEFAULT_WEIGHT_KG = 70.0


def get_weight(user: User) -> float:
    if user and user.weight_kg:
        return user.weight_kg
    return DEFAULT_WEIGHT_KG


async def log_exercise(db: AsyncSession, req: ExerciseLogRequest, user: User) -> ExerciseEntry:
    weight_kg = get_weight(user)
    if req.calories_burned_override is not None:
        calories = req.calories_burned_override
    else:
        calories = _engine.calculate_exercise_calories(
            req.name, req.intensity, req.duration_minutes, weight_kg
        )
    entry = ExerciseEntry(
        user_id=user.id,
        name=req.name,
        duration_minutes=req.duration_minutes,
        intensity=req.intensity,
        calories_burned=calories,
        date=req.date or datetime.date.today(),
        logged_at=datetime.datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_today(db: AsyncSession, user: User) -> dict:
    today = datetime.date.today()
    result = await db.execute(
        select(ExerciseEntry)
        .where(ExerciseEntry.user_id == user.id, ExerciseEntry.date == today)
        .order_by(ExerciseEntry.id.desc())
    )
    entries = result.scalars().all()
    return {
        "entries": entries,
        "total_burned": round(sum(e.calories_burned for e in entries), 1),
    }


async def get_entries(db: AsyncSession, date: datetime.date | None, user: User) -> list[ExerciseEntry]:
    query = select(ExerciseEntry).where(ExerciseEntry.user_id == user.id)
    if date:
        query = query.where(ExerciseEntry.date == date)
    result = await db.execute(query.order_by(ExerciseEntry.id.desc()))
    return result.scalars().all()


async def delete_entry(db: AsyncSession, entry_id: int, user: User) -> None:
    """Raises ValueError if the entry does not exist or belongs to another user."""
    result = await db.execute(
        select(ExerciseEntry).where(
            ExerciseEntry.id == entry_id, ExerciseEntry.user_id == user.id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise ValueError(f"Exercise entry {entry_id} not found")
    await db.delete(entry)
    await db.commit()
