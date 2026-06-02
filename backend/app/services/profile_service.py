from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.services.calorie_engine import calculate_daily_goal


async def get_or_create_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        user = User()
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


def is_setup(user: User) -> bool:
    return all([
        user.age is not None,
        user.gender is not None,
        user.height_cm is not None,
        user.weight_kg is not None,
        user.aim is not None,
    ])


def cuisine_to_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [c for c in raw.split("|") if c]


def list_to_cuisine(cuisines: list[str] | None) -> str | None:
    if not cuisines:
        return None
    return "|".join(cuisines)


def build_profile_response(user: User) -> dict:
    setup = is_setup(user)
    return {
        "id": user.id,
        "name": user.name or "",
        "email": user.email,
        "age": user.age,
        "gender": user.gender,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "activity_level": user.activity_level or "moderate",
        "aim": user.aim,
        "goal_calories": user.goal_calories or 2000,
        "is_setup": setup,
        "goals": calculate_daily_goal(user) if setup else None,
        "dietary_preference": user.dietary_preference,
        "cuisine_preferences": cuisine_to_list(user.cuisine_preferences),
    }
