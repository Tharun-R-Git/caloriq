import asyncio
import base64
import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

try:
    from mistralai.client import Mistral
    _MISTRAL_AVAILABLE = True
except ImportError:
    Mistral = None
    _MISTRAL_AVAILABLE = False

_MODEL = "mistral-small-latest"
_VISION_MODEL = "pixtral-12b-2409"


class GeminiService:
    """AI service — backed by Mistral AI. Name kept for import compatibility."""

    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY", "").strip('"').strip("'")
        if _MISTRAL_AVAILABLE and api_key:
            self.client = Mistral(api_key=api_key)
        else:
            self.client = None

    def _call_mistral(self, prompt: str) -> str:
        response = self.client.chat.complete(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=512,
        )
        return response.choices[0].message.content

    @staticmethod
    def _strip_markdown(text: str) -> str:
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        return text.strip()

    # ── Food analysis ────────────────────────────────────────────────────────

    def _mock_analyze(self, name: str) -> dict[str, Any]:
        n = name.lower()
        if any(w in n for w in ["biryani", "rice", "pulao"]):
            return {"calories": 450, "protein_g": 12.0, "carbs_g": 72.0, "fat_g": 14.0, "serving_size": "1 plate (350g)", "confidence": 0.0}
        if any(w in n for w in ["chicken", "mutton", "fish", "egg"]):
            return {"calories": 280, "protein_g": 32.0, "carbs_g": 6.0, "fat_g": 14.0, "serving_size": "1 serving (200g)", "confidence": 0.0}
        if any(w in n for w in ["pizza", "burger", "sandwich"]):
            return {"calories": 520, "protein_g": 22.0, "carbs_g": 58.0, "fat_g": 22.0, "serving_size": "1 piece", "confidence": 0.0}
        if any(w in n for w in ["dal", "lentil", "soup"]):
            return {"calories": 180, "protein_g": 10.0, "carbs_g": 28.0, "fat_g": 4.0, "serving_size": "1 bowl (250ml)", "confidence": 0.0}
        if any(w in n for w in ["roti", "chapati", "naan", "bread"]):
            return {"calories": 120, "protein_g": 4.0, "carbs_g": 22.0, "fat_g": 3.0, "serving_size": "1 piece (60g)", "confidence": 0.0}
        if any(w in n for w in ["salad", "vegetable", "veg"]):
            return {"calories": 80, "protein_g": 3.0, "carbs_g": 12.0, "fat_g": 2.0, "serving_size": "1 bowl (200g)", "confidence": 0.0}
        if any(w in n for w in ["coffee", "tea", "juice", "milk"]):
            return {"calories": 60, "protein_g": 2.0, "carbs_g": 10.0, "fat_g": 1.5, "serving_size": "1 cup (240ml)", "confidence": 0.0}
        return {"calories": 300, "protein_g": 10.0, "carbs_g": 40.0, "fat_g": 10.0, "serving_size": "1 serving", "confidence": 0.0}

    async def analyze_food(self, name: str, description: str = None) -> dict[str, Any]:
        if not self.client:
            return self._mock_analyze(name)

        desc_part = description or "no additional info"
        prompt = (
            "Analyze this food and return ONLY a JSON object with these exact keys: "
            "calories (int), protein_g (float), carbs_g (float), fat_g (float), "
            "serving_size (str), confidence (float 0-1). "
            "Return ONLY valid JSON, no markdown, no explanation. "
            f"Food: {name}. Additional info: {desc_part}"
        )
        try:
            text = self._strip_markdown(await asyncio.to_thread(self._call_mistral, prompt))
            data = json.loads(text)
            confidence = float(data.get("confidence", 0.5))
            return {
                "calories": int(data["calories"]),
                "protein_g": float(data.get("protein_g", 0)),
                "carbs_g": float(data.get("carbs_g", 0)),
                "fat_g": float(data.get("fat_g", 0)),
                "serving_size": str(data.get("serving_size", "")),
                "confidence": max(0.0, min(1.0, confidence)),
            }
        except Exception as exc:
            logger.warning("Mistral analyze_food failed for %r: %s", name, exc)
            return self._mock_analyze(name)

    # ── Photo analysis ───────────────────────────────────────────────────────

    def _mock_analyze_photo(self, not_available: bool = False) -> dict[str, Any]:
        return {
            "calories": 350,
            "protein_g": 12.0,
            "carbs_g": 45.0,
            "fat_g": 10.0,
            "food_name": "Mixed food plate",
            "serving_size": "1 plate",
            "confidence": 0.0,
            "items_detected": [],
            "not_available": not_available,
        }

    async def analyze_food_photo(self, image_base64: str, mime_type: str) -> dict[str, Any]:
        if not self.client:
            return self._mock_analyze_photo(not_available=True)

        prompt = (
            "Analyze this food image and return ONLY a JSON object with these exact keys: "
            "calories (int), protein_g (float), carbs_g (float), fat_g (float), "
            "food_name (str), serving_size (str), confidence (float 0-1), "
            "items_detected (list of strings for each food item you can see). "
            "Return only valid JSON, no markdown, no explanation."
        )
        try:
            image_b64_str = base64.b64encode(base64.b64decode(image_base64)).decode("utf-8")
            response = await asyncio.to_thread(
                self.client.chat.complete,
                model=_VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64_str}"}},
                        {"type": "text", "text": prompt},
                    ],
                }],
                temperature=0.1,
                max_tokens=512,
            )
            text = self._strip_markdown(response.choices[0].message.content)
            data = json.loads(text)
            confidence = float(data.get("confidence", 0.5))
            return {
                "calories": int(data["calories"]),
                "protein_g": float(data.get("protein_g", 0)),
                "carbs_g": float(data.get("carbs_g", 0)),
                "fat_g": float(data.get("fat_g", 0)),
                "food_name": str(data.get("food_name", "Unknown food")),
                "serving_size": str(data.get("serving_size", "")),
                "confidence": max(0.0, min(1.0, confidence)),
                "items_detected": list(data.get("items_detected", [])),
                "not_available": False,
            }
        except Exception as exc:
            logger.warning("Mistral analyze_food_photo failed: %s", exc)
            # Vision not supported or model error — notify the frontend
            return self._mock_analyze_photo(not_available=True)

    # ── Exercise analysis ────────────────────────────────────────────────────

    def _mock_analyze_exercise(self, description: str, duration_minutes: float) -> dict[str, Any]:
        d = description.lower()
        if any(w in d for w in ["run", "jog", "sprint"]):
            met = 9.0; etype = "cardio"; intensity = "vigorous"
        elif any(w in d for w in ["walk", "stroll"]):
            met = 3.5; etype = "cardio"; intensity = "light"
        elif any(w in d for w in ["cycle", "bike", "cycling"]):
            met = 8.0; etype = "cardio"; intensity = "moderate"
        elif any(w in d for w in ["swim", "swimming"]):
            met = 7.0; etype = "cardio"; intensity = "moderate"
        elif any(w in d for w in ["gym", "weight", "lift", "strength"]):
            met = 5.0; etype = "strength"; intensity = "moderate"
        elif any(w in d for w in ["yoga", "stretch"]):
            met = 2.5; etype = "flexibility"; intensity = "light"
        elif any(w in d for w in ["hiit", "circuit", "intense"]):
            met = 10.0; etype = "cardio"; intensity = "vigorous"
        else:
            met = 5.0; etype = "cardio"; intensity = "moderate"
        calories = round(met * 70.0 * (duration_minutes / 60), 1)
        return {"calories_burned": calories, "exercise_type": etype, "met_value": met, "intensity": intensity, "confidence": 0.0}

    async def analyze_exercise(self, description: str, duration_minutes: float, weight_kg: float = 70.0) -> dict[str, Any]:
        if not self.client:
            return self._mock_analyze_exercise(description, duration_minutes)

        prompt = (
            f"Estimate calories burned for this exercise. User weight: {weight_kg}kg, Duration: {duration_minutes} minutes. "
            f"Exercise: {description}. "
            "Consider all details provided (distance, pace, terrain, equipment, etc.) for accuracy. "
            "Return ONLY valid JSON, no markdown, no explanation: "
            '{"calories_burned": 0, "exercise_type": "cardio", "met_value": 0.0, "intensity": "moderate", "confidence": 0.0}'
        )
        try:
            text = self._strip_markdown(await asyncio.to_thread(self._call_mistral, prompt))
            data = json.loads(text)
            return {
                "calories_burned": round(float(data.get("calories_burned", 0)), 1),
                "exercise_type": str(data.get("exercise_type", "cardio")),
                "met_value": float(data.get("met_value", 5.0)),
                "intensity": str(data.get("intensity", "moderate")),
                "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
            }
        except Exception as exc:
            logger.warning("Mistral analyze_exercise failed: %s", exc)
            return self._mock_analyze_exercise(description, duration_minutes)

    # ── Meal recommendations ─────────────────────────────────────────────────

    async def get_meal_ideas(self, calorie_target: int, dietary_preferences: list[str]) -> list[dict]:
        return []

    def _mock_recommendations(self, time_of_day: str) -> dict:
        if "morning" in time_of_day:
            return {"recommendations": [
                {"name": "Oatmeal with banana", "calories": 320, "protein_g": 10.0, "carbs_g": 58.0, "fat_g": 5.0, "reason": "High-fibre morning fuel", "portion_size": "1 bowl (300g)"},
                {"name": "Greek yogurt with honey", "calories": 180, "protein_g": 15.0, "carbs_g": 20.0, "fat_g": 3.0, "reason": "Protein-rich light breakfast", "portion_size": "200g"},
                {"name": "Boiled eggs on toast", "calories": 280, "protein_g": 18.0, "carbs_g": 24.0, "fat_g": 10.0, "reason": "Balanced protein and carbs to start the day", "portion_size": "2 eggs + 1 slice"},
            ], "exercise_suggestions": []}
        if "lunch" in time_of_day or "afternoon" in time_of_day:
            return {"recommendations": [
                {"name": "Grilled chicken salad", "calories": 350, "protein_g": 40.0, "carbs_g": 15.0, "fat_g": 12.0, "reason": "High protein mid-day meal", "portion_size": "1 large bowl"},
                {"name": "Dal and roti", "calories": 380, "protein_g": 18.0, "carbs_g": 58.0, "fat_g": 8.0, "reason": "Balanced Indian staple", "portion_size": "2 rotis + 1 bowl dal"},
                {"name": "Tuna whole-wheat sandwich", "calories": 420, "protein_g": 32.0, "carbs_g": 42.0, "fat_g": 10.0, "reason": "Portable protein-packed lunch", "portion_size": "1 sandwich"},
            ], "exercise_suggestions": []}
        if "dinner" in time_of_day or "evening" in time_of_day:
            return {"recommendations": [
                {"name": "Baked salmon with vegetables", "calories": 400, "protein_g": 38.0, "carbs_g": 20.0, "fat_g": 18.0, "reason": "Omega-3 rich satisfying dinner", "portion_size": "200g salmon + 1 cup veg"},
                {"name": "Paneer curry with brown rice", "calories": 450, "protein_g": 22.0, "carbs_g": 55.0, "fat_g": 16.0, "reason": "Filling vegetarian dinner", "portion_size": "1 cup rice + 1 cup curry"},
                {"name": "Vegetable soup with bread", "calories": 250, "protein_g": 8.0, "carbs_g": 38.0, "fat_g": 6.0, "reason": "Light, low-calorie evening option", "portion_size": "1 bowl + 1 slice bread"},
            ], "exercise_suggestions": []}
        return {"recommendations": [
            {"name": "Cottage cheese with nuts", "calories": 200, "protein_g": 18.0, "carbs_g": 8.0, "fat_g": 10.0, "reason": "Light protein-rich snack", "portion_size": "100g cottage cheese + 15g nuts"},
            {"name": "Mixed nuts", "calories": 180, "protein_g": 6.0, "carbs_g": 8.0, "fat_g": 15.0, "reason": "Healthy fats with minimal carbs", "portion_size": "30g"},
            {"name": "Banana with peanut butter", "calories": 220, "protein_g": 7.0, "carbs_g": 30.0, "fat_g": 8.0, "reason": "Quick energy with protein", "portion_size": "1 medium banana + 1 tbsp PB"},
        ], "exercise_suggestions": []}

    async def get_meal_recommendations(
        self,
        user_profile: dict,
        remaining_calories: int,
        remaining_protein: float,
        remaining_carbs: float,
        remaining_fat: float,
        recent_foods: list[str],
        time_of_day: str,
        meal_source: str = "home",
    ) -> dict:
        if not self.client:
            return self._mock_recommendations(time_of_day)

        age = user_profile.get("age") or "unknown"
        weight = user_profile.get("weight_kg") or "unknown"
        goal = user_profile.get("goal_calories", 2000)
        activity = user_profile.get("activity_level", "moderate")
        dietary = user_profile.get("dietary_preference") or "no preference"
        cuisines = user_profile.get("cuisine_preferences") or []
        cuisine_str = ", ".join(cuisines) if cuisines else "no preference"
        recent_str = ", ".join(recent_foods) if recent_foods else "nothing yet"
        over_goal = remaining_calories < 0
        excess = abs(remaining_calories) if over_goal else 0

        is_home = meal_source != "restaurant"
        source_instruction = (
            "Suggest simple HOME COOKING meals that are easy to prepare with common ingredients — "
            "think everyday dishes, minimal prep, realistic for someone cooking at home. "
            "Avoid complex recipes or restaurant-style plating."
            if is_home else
            "Suggest RESTAURANT ORDER meals — dishes worth ordering out, flavourful and satisfying. "
            "Think popular restaurant items, street food, or café picks that are hard to replicate at home."
        )

        if over_goal:
            prompt = (
                f"User profile: {age}y, {weight}kg, goal: {goal} kcal/day, activity: {activity}. "
                f"Dietary preference: {dietary}. Preferred cuisines: {cuisine_str}. "
                f"The user has EXCEEDED their calorie goal by {excess} kcal today. "
                f"Recently eaten: {recent_str}. Time of day: {time_of_day}. "
                f"{source_instruction} "
                "Suggest 2 very light food options to minimize further excess, and 2 exercises to burn off the extra calories. "
                "Return ONLY valid JSON, no markdown, no explanation: "
                '{"recommendations": [{"name": "string", "calories": 0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "reason": "string", "portion_size": "string"}], '
                '"exercise_suggestions": [{"name": "string", "duration_minutes": 30, "calories_burned": 0, "reason": "string"}]}'
            )
        else:
            prompt = (
                f"User profile: {age}y, {weight}kg, goal: {goal} kcal/day, activity: {activity}. "
                f"Dietary preference: {dietary}. Preferred cuisines: {cuisine_str}. "
                f"Remaining today: {remaining_calories} kcal, {remaining_protein}g protein, "
                f"{remaining_carbs}g carbs, {remaining_fat}g fat. "
                f"Recently eaten: {recent_str}. Time of day: {time_of_day}. "
                f"{source_instruction} "
                "Suggest 3 specific meals/snacks that match the dietary preference, preferred cuisines, and remaining macros. "
                "Return ONLY valid JSON, no markdown, no explanation: "
                '{"recommendations": [{"name": "string", "calories": 0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "reason": "string", "portion_size": "string"}], '
                '"exercise_suggestions": []}'
            )

        try:
            text = self._strip_markdown(await asyncio.to_thread(self._call_mistral, prompt))
            data = json.loads(text)
            recs = []
            for r in data.get("recommendations", [])[:3]:
                recs.append({
                    "name": str(r.get("name", "")),
                    "calories": int(r.get("calories", 0)),
                    "protein_g": float(r.get("protein_g", 0)),
                    "carbs_g": float(r.get("carbs_g", 0)),
                    "fat_g": float(r.get("fat_g", 0)),
                    "reason": str(r.get("reason", "")),
                    "portion_size": str(r.get("portion_size", "1 serving")),
                })
            exercises = []
            for e in data.get("exercise_suggestions", [])[:2]:
                exercises.append({
                    "name": str(e.get("name", "")),
                    "duration_minutes": int(e.get("duration_minutes", 30)),
                    "calories_burned": int(e.get("calories_burned", 0)),
                    "reason": str(e.get("reason", "")),
                })
            return {"recommendations": recs, "exercise_suggestions": exercises}
        except Exception as exc:
            logger.warning("Mistral get_meal_recommendations failed: %s", exc)
            return self._mock_recommendations(time_of_day)
