import pytest
from unittest.mock import AsyncMock, patch

MOCK_RECS = {
    "recommendations": [
        {
            "name": "Grilled chicken salad",
            "calories": 350,
            "protein_g": 40.0,
            "carbs_g": 15.0,
            "fat_g": 12.0,
            "reason": "High protein mid-day meal",
            "portion_size": "1 large bowl",
        },
        {
            "name": "Dal and roti",
            "calories": 380,
            "protein_g": 18.0,
            "carbs_g": 58.0,
            "fat_g": 8.0,
            "reason": "Balanced Indian staple",
            "portion_size": "2 rotis + 1 bowl dal",
        },
        {
            "name": "Greek yogurt",
            "calories": 180,
            "protein_g": 15.0,
            "carbs_g": 20.0,
            "fat_g": 3.0,
            "reason": "Protein snack",
            "portion_size": "200g",
        },
    ],
    "remaining_calories": 800,
    "message": "Based on your remaining 800 kcal for today",
}


# ---------------------------------------------------------------------------
# GET /api/ai/recommendations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_recommendations_returns_correct_shape(client):
    with patch(
        "app.routes.ai.RecommendationService.get_meal_recommendations",
        new_callable=AsyncMock,
        return_value=MOCK_RECS,
    ):
        resp = await client.get("/api/ai/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert "remaining_calories" in data
    assert "message" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) == 3


@pytest.mark.asyncio
async def test_recommendations_each_item_has_required_fields(client):
    with patch(
        "app.routes.ai.RecommendationService.get_meal_recommendations",
        new_callable=AsyncMock,
        return_value=MOCK_RECS,
    ):
        resp = await client.get("/api/ai/recommendations")
    recs = resp.json()["recommendations"]
    required = {"name", "calories", "protein_g", "carbs_g", "fat_g", "reason", "portion_size"}
    for rec in recs:
        assert required.issubset(rec.keys()), f"Missing keys in {rec}"


@pytest.mark.asyncio
async def test_recommendations_no_profile_uses_defaults(client):
    """With no profile / food logs, returns 3 mock recommendations."""
    resp = await client.get("/api/ai/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["recommendations"]) == 3
    assert data["remaining_calories"] >= 0


@pytest.mark.asyncio
async def test_recommendations_remaining_calories_decreases_after_food_log(client):
    baseline = await client.get("/api/ai/recommendations")
    baseline_remaining = baseline.json()["remaining_calories"]

    await client.post(
        "/api/food/log",
        json={"name": "oatmeal", "calories": 400, "protein_g": 8.0, "carbs_g": 72.0, "fat_g": 5.0},
    )

    after = await client.get("/api/ai/recommendations")
    assert after.status_code == 200
    assert after.json()["remaining_calories"] < baseline_remaining


@pytest.mark.asyncio
async def test_recommendations_message_present(client):
    resp = await client.get("/api/ai/recommendations")
    assert isinstance(resp.json()["message"], str)
    assert len(resp.json()["message"]) > 0
