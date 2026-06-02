import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.food_entry import FoodEntry
from app.models.exercise_entry import ExerciseEntry
from app.routes.profile import get_or_create_user


async def get_daily_summary(db: AsyncSession) -> dict:
    today = datetime.date.today()

    food_res = await db.execute(
        select(
            func.coalesce(func.sum(FoodEntry.calories), 0),
            func.coalesce(func.sum(FoodEntry.protein_g), 0),
            func.coalesce(func.sum(FoodEntry.carbs_g), 0),
            func.coalesce(func.sum(FoodEntry.fat_g), 0),
        ).where(FoodEntry.date == today)
    )
    calories_in, protein_g, carbs_g, fat_g = food_res.one()

    ex_res = await db.execute(
        select(func.coalesce(func.sum(ExerciseEntry.calories_burned), 0)).where(
            ExerciseEntry.date == today
        )
    )
    calories_burned = ex_res.scalar()

    user = await get_or_create_user(db)
    daily_goal = user.goal_calories or 2000

    net_calories = round(float(calories_in) - float(calories_burned))
    remaining = daily_goal - net_calories

    # Last 3 unique food names across recent history (most recently logged first)
    rows = await db.execute(
        select(
            FoodEntry.name,
            FoodEntry.calories,
            FoodEntry.protein_g,
            FoodEntry.carbs_g,
            FoodEntry.fat_g,
        ).order_by(desc(FoodEntry.logged_at)).limit(30)
    )
    seen: set[str] = set()
    recent_foods = []
    for name, cal, prot, carbs, fat in rows.all():
        if name not in seen:
            seen.add(name)
            recent_foods.append(
                {
                    "name": name,
                    "calories": round(float(cal), 1),
                    "protein_g": round(float(prot or 0), 1),
                    "carbs_g": round(float(carbs or 0), 1),
                    "fat_g": round(float(fat or 0), 1),
                }
            )
        if len(recent_foods) == 3:
            break

    return {
        "calories_in": round(float(calories_in)),
        "calories_burned": round(float(calories_burned)),
        "net_calories": net_calories,
        "daily_goal": daily_goal,
        "remaining": remaining,
        "protein_g": round(float(protein_g), 1),
        "carbs_g": round(float(carbs_g), 1),
        "fat_g": round(float(fat_g), 1),
        "recent_foods": recent_foods,
    }
