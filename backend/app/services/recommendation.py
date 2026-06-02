from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.profile import get_or_create_user
from app.services.calorie_engine import CalorieEngine


class RecommendationService:
    def __init__(self):
        self.engine = CalorieEngine()

    async def get_suggestions(self, db: AsyncSession) -> dict:
        # TODO: analyze recent food/exercise logs before generating tips
        user = await get_or_create_user(db)
        suggestions = []

        if user.weight_kg and user.height_cm and user.age:
            bmr = self.engine.calculate_bmr(user.weight_kg, user.height_cm, user.age)
            tdee = self.engine.calculate_tdee(bmr, user.activity_level)
            suggestions.append(f"Your estimated daily calorie need (TDEE) is {tdee} kcal.")

        if not suggestions:
            suggestions.append("Complete your profile to get personalized recommendations.")

        suggestions.append("TODO: analyze recent logs and surface personalized nutrition tips.")

        return {"suggestions": suggestions, "user_id": user.id}
