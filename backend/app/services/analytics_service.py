import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.food_entry import FoodEntry
from app.models.exercise_entry import ExerciseEntry
from app.models.user import User
from app.schemas.analytics import DailyResponse, TrendDay


async def get_daily_summary(db: AsyncSession, user: User) -> dict:
    today = datetime.date.today()

    food_res = await db.execute(
        select(
            func.coalesce(func.sum(FoodEntry.calories), 0),
            func.coalesce(func.sum(FoodEntry.protein_g), 0),
            func.coalesce(func.sum(FoodEntry.carbs_g), 0),
            func.coalesce(func.sum(FoodEntry.fat_g), 0),
        ).where(FoodEntry.user_id == user.id, FoodEntry.date == today)
    )
    calories_in, protein_g, carbs_g, fat_g = food_res.one()

    ex_res = await db.execute(
        select(func.coalesce(func.sum(ExerciseEntry.calories_burned), 0)).where(
            ExerciseEntry.user_id == user.id, ExerciseEntry.date == today
        )
    )
    calories_burned = ex_res.scalar()

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
        )
        .where(FoodEntry.user_id == user.id)
        .order_by(desc(FoodEntry.logged_at))
        .limit(30)
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
        "protein_goal_g": round(daily_goal * 0.30 / 4),
        "carbs_goal_g": round(daily_goal * 0.45 / 4),
        "fat_goal_g": round(daily_goal * 0.25 / 9),
        "recent_foods": recent_foods,
    }


async def get_daily_for_date(db: AsyncSession, date: datetime.date, user: User) -> DailyResponse:
    food_res = await db.execute(
        select(
            func.coalesce(func.sum(FoodEntry.calories), 0),
            func.coalesce(func.sum(FoodEntry.protein_g), 0),
            func.coalesce(func.sum(FoodEntry.carbs_g), 0),
            func.coalesce(func.sum(FoodEntry.fat_g), 0),
        ).where(FoodEntry.user_id == user.id, FoodEntry.date == date)
    )
    cal, protein, carbs, fat = food_res.one()

    ex_res = await db.execute(
        select(func.coalesce(func.sum(ExerciseEntry.calories_burned), 0)).where(
            ExerciseEntry.user_id == user.id, ExerciseEntry.date == date
        )
    )
    burned = ex_res.scalar()

    return DailyResponse(
        date=date,
        calories_in=round(float(cal), 1),
        calories_burned=round(float(burned), 1),
        protein_g=round(float(protein), 1),
        carbs_g=round(float(carbs), 1),
        fat_g=round(float(fat), 1),
        goal=user.goal_calories or 2000,
    )


async def get_trends(db: AsyncSession, days: int, user: User) -> list[TrendDay]:
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days - 1)

    food_rows = await db.execute(
        select(
            FoodEntry.date,
            func.coalesce(func.sum(FoodEntry.calories), 0).label("calories_in"),
            func.coalesce(func.sum(FoodEntry.protein_g), 0).label("protein_g"),
            func.coalesce(func.sum(FoodEntry.carbs_g), 0).label("carbs_g"),
            func.coalesce(func.sum(FoodEntry.fat_g), 0).label("fat_g"),
        )
        .where(FoodEntry.user_id == user.id, FoodEntry.date >= start)
        .group_by(FoodEntry.date)
    )
    food_by_date = {row.date: row for row in food_rows.all()}

    ex_rows = await db.execute(
        select(
            ExerciseEntry.date,
            func.coalesce(func.sum(ExerciseEntry.calories_burned), 0).label("calories_burned"),
        )
        .where(ExerciseEntry.user_id == user.id, ExerciseEntry.date >= start)
        .group_by(ExerciseEntry.date)
    )
    ex_by_date = {row.date: row for row in ex_rows.all()}

    goal = user.goal_calories or 2000

    result = []
    for i in range(days):
        d = start + datetime.timedelta(days=i)
        food = food_by_date.get(d)
        ex = ex_by_date.get(d)

        cal_in = round(float(food.calories_in), 1) if food else 0.0
        cal_burned = round(float(ex.calories_burned), 1) if ex else 0.0

        result.append(TrendDay(
            date=str(d),
            calories_in=cal_in,
            calories_burned=cal_burned,
            net=round(cal_in - cal_burned, 1),
            protein_g=round(float(food.protein_g), 1) if food else 0.0,
            carbs_g=round(float(food.carbs_g), 1) if food else 0.0,
            fat_g=round(float(food.fat_g), 1) if food else 0.0,
            goal=goal,
        ))

    return result
