import pytest
from unittest.mock import AsyncMock, patch


MOCK_ANALYSIS = {
    "calories": 450,
    "protein_g": 12.0,
    "carbs_g": 72.0,
    "fat_g": 14.0,
    "serving_size": "1 plate (350g)",
    "confidence": 0.85,
}


# ---------------------------------------------------------------------------
# POST /api/food/analyze
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_analyze_food_happy_path(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food",
        new_callable=AsyncMock,
        return_value=MOCK_ANALYSIS,
    ):
        resp = await client.post("/api/food/analyze", json={"name": "chicken biryani"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["calories"] == 450
    assert data["protein_g"] == 12.0
    assert "serving_size" in data


@pytest.mark.asyncio
async def test_analyze_food_missing_name(client):
    resp = await client.post("/api/food/analyze", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_food_gemini_failure_returns_mock(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food",
        new_callable=AsyncMock,
        side_effect=Exception("quota exceeded"),
    ):
        resp = await client.post("/api/food/analyze", json={"name": "pizza"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["calories"] > 0


# ---------------------------------------------------------------------------
# POST /api/food/log
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_log_food_happy_path(client):
    payload = {
        "name": "chicken biryani",
        "calories": 450,
        "protein_g": 12.0,
        "carbs_g": 72.0,
        "fat_g": 14.0,
        "serving_size": "1 plate",
    }
    resp = await client.post("/api/food/log", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["name"] == "chicken biryani"
    assert data["calories"] == 450


@pytest.mark.asyncio
async def test_log_food_missing_calories(client):
    resp = await client.post("/api/food/log", json={"name": "pizza"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_log_food_missing_name(client):
    resp = await client.post("/api/food/log", json={"calories": 300})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/food/today
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_today_empty(client):
    resp = await client.get("/api/food/today")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_today_returns_logged_entries(client):
    await client.post("/api/food/log", json={"name": "dosa", "calories": 180})
    resp = await client.get("/api/food/today")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "dosa"


# ---------------------------------------------------------------------------
# DELETE /api/food/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_food_entry(client):
    log = await client.post("/api/food/log", json={"name": "idli", "calories": 80})
    entry_id = log.json()["id"]

    resp = await client.delete(f"/api/food/{entry_id}")
    assert resp.status_code == 204

    today = await client.get("/api/food/today")
    assert all(e["id"] != entry_id for e in today.json())


@pytest.mark.asyncio
async def test_delete_nonexistent_entry(client):
    resp = await client.delete("/api/food/99999")
    assert resp.status_code == 404
