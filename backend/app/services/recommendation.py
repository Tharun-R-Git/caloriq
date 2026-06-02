import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.profile_service import get_or_create_user, cuisine_to_list
from app.services.analytics_service import get_daily_summary
from app.services.gemini_service import GeminiService


class RecommendationService:
    def __init__(self):
        self.gemini = GeminiService()

    def _time_of_day(self) -> str:
        hour = datetime.datetime.now().hour
        if hour < 10:
            return "morning"
        if hour < 13:
            return "late morning / lunch"
        if hour < 17:
            return "afternoon"
        if hour < 21:
            return "evening / dinner"
        return "night"

    def _goal_macros(self, goal_calories: int) -> tuple[float, float, float]:
        protein_g = round(goal_calories * 0.30 / 4, 1)
        carbs_g = round(goal_calories * 0.40 / 4, 1)
        fat_g = round(goal_calories * 0.30 / 9, 1)
        return protein_g, carbs_g, fat_g

    async def get_meal_recommendations(self, db: AsyncSession, meal_source: str = "home") -> dict:
        user = await get_or_create_user(db)
        summary = await get_daily_summary(db)

        goal_calories = user.goal_calories or 2000
        goal_protein, goal_carbs, goal_fat = self._goal_macros(goal_calories)

        # Allow negative remaining to signal over-goal
        remaining_calories = summary["remaining"]
        remaining_protein = round(max(0.0, goal_protein - summary["protein_g"]), 1)
        remaining_carbs = round(max(0.0, goal_carbs - summary["carbs_g"]), 1)
        remaining_fat = round(max(0.0, goal_fat - summary["fat_g"]), 1)
        over_goal = remaining_calories < 0

        recent_foods = [f["name"] for f in summary["recent_foods"]]
        time_of_day = self._time_of_day()

        user_profile = {
            "age": user.age,
            "weight_kg": user.weight_kg,
            "goal_calories": goal_calories,
            "activity_level": user.activity_level,
            "dietary_preference": user.dietary_preference,
            "cuisine_preferences": cuisine_to_list(user.cuisine_preferences),
        }

        result = await self.gemini.get_meal_recommendations(
            user_profile=user_profile,
            remaining_calories=remaining_calories,
            remaining_protein=remaining_protein,
            remaining_carbs=remaining_carbs,
            remaining_fat=remaining_fat,
            recent_foods=recent_foods,
            time_of_day=time_of_day,
            meal_source=meal_source,
        )

        if over_goal:
            message = f"You're {abs(remaining_calories)} kcal over your goal — try lighter options and some exercise."
        elif remaining_calories == 0:
            message = "You've hit your calorie goal — here are some light options."
        else:
            message = f"You have {remaining_calories} kcal remaining for today."

        return {
            "recommendations": result.get("recommendations", []),
            "exercise_suggestions": result.get("exercise_suggestions", []),
            "remaining_calories": remaining_calories,
            "over_goal": over_goal,
            "message": message,
        }

    async def get_suggestions(self, db: AsyncSession) -> dict:
        from app.services.calorie_engine import CalorieEngine

        engine = CalorieEngine()
        user = await get_or_create_user(db)
        suggestions = []

        if user.weight_kg and user.height_cm and user.age:
            bmr = engine.calculate_bmr(user.weight_kg, user.height_cm, user.age)
            tdee = engine.calculate_tdee(bmr, user.activity_level)
            suggestions.append(f"Your estimated daily calorie need (TDEE) is {tdee} kcal.")

        if not suggestions:
            suggestions.append("Complete your profile to get personalized recommendations.")

        return {"suggestions": suggestions, "user_id": user.id}
