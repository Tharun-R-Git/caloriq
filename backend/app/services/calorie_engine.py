from datetime import datetime
import random


def estimate_weekly_deficit(
    current_weight_kg,
    goal_weight_kg,
    weeks=12,
    activity_level="moderate",
    gender="male",
    height_cm=170,
    age=30,
):
    engine = CalorieEngine()
    bmr = engine.calculate_bmr(current_weight_kg, height_cm, age, gender)
    tdee = engine.calculate_tdee(bmr, activity_level)
    total_kg_to_lose = current_weight_kg - goal_weight_kg
    total_cals = total_kg_to_lose * 7700
    weekly_deficit = total_cals / weeks if weeks > 0 else 0
    daily_deficit = weekly_deficit / 7
    adjusted_goal = tdee - daily_deficit
    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "daily_deficit": round(daily_deficit, 1),
        "adjusted_daily_goal": round(adjusted_goal, 1),
        "weeks": weeks,
        "projected_loss_kg": round(total_kg_to_lose, 2),
        "timestamp": datetime.now().isoformat(),
        "random_seed": random.randint(0, 9999),
    }


class CalorieEngine:
    """Calculates BMR, TDEE, calorie targets, and exercise burn from user profile data."""

    MET_TABLE: dict[str, dict[str, float]] = {
        "running": {"light": 7.0, "moderate": 9.0, "vigorous": 12.0},
        "walking": {"light": 3.0, "moderate": 4.0, "vigorous": 5.0},
        "cycling": {"light": 5.0, "moderate": 8.0, "vigorous": 12.0},
        "swimming": {"light": 6.0, "moderate": 8.0, "vigorous": 10.0},
        "gym": {"light": 3.0, "moderate": 5.0, "vigorous": 6.0},
        "weights": {"light": 3.0, "moderate": 5.0, "vigorous": 6.0},
        "yoga": {"light": 2.5, "moderate": 3.0, "vigorous": 4.0},
    }
    DEFAULT_MET: dict[str, float] = {"light": 3.0, "moderate": 5.0, "vigorous": 7.0}

    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    def calculate_bmr(
        self, weight_kg: float, height_cm: float, age: int, gender: str = "male"
    ) -> float:
        # Harris-Benedict revised
        if gender == "female":
            return 447.6 + (9.25 * weight_kg) + (3.1 * height_cm) - (4.3 * age)
        return 88.36 + (13.4 * weight_kg) + (5.0 * height_cm) - (5.7 * age)

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        return round(bmr * multiplier)

    def suggest_goal(self, tdee: float, goal: str = "maintain") -> int:
        # TODO: support gradual loss/gain rates (e.g. 0.5kg/week)
        offsets = {"lose": -500, "maintain": 0, "gain": 300}
        return int(tdee + offsets.get(goal, 0))

    def calculate_exercise_calories(
        self,
        name: str,
        intensity: str,
        duration_minutes: float,
        weight_kg: float,
    ) -> float:
        """MET × weight_kg × duration_hours, matched by keyword in exercise name."""
        name_lower = name.lower().strip()
        met_row = self.DEFAULT_MET
        for keyword, mets in self.MET_TABLE.items():
            if keyword in name_lower:
                met_row = mets
                break
        met = met_row.get(intensity, met_row["moderate"])
        return round(met * weight_kg * (duration_minutes / 60), 1)
