import asyncio
import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

try:
    from google import genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip('"').strip("'")
        if _GENAI_AVAILABLE and api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    def _call_gemini(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"timeout": 10},
        )
        return response.text

    def _mock_analyze(self, name: str) -> dict[str, Any]:
        """Realistic mock data keyed on common food keywords."""
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
            text = await asyncio.to_thread(self._call_gemini, prompt)
            text = text.strip()
            text = re.sub(r'^```(?:json)?\s*\n?', '', text)
            text = re.sub(r'\n?```\s*$', '', text)
            text = text.strip()
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
            logger.warning("Gemini analyze_food failed for %r: %s", name, exc)
            return self._mock_analyze(name)

    async def get_meal_ideas(self, calorie_target: int, dietary_preferences: list[str]) -> list[dict]:
        # TODO: generate meal suggestions using Gemini
        return []
