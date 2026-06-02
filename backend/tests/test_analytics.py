import pytest


@pytest.mark.asyncio
async def test_daily_summary_empty(client):
    resp = await client.get("/api/analytics/daily-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["calories_in"] == 0
    assert data["calories_burned"] == 0
    assert data["net_calories"] == 0
    assert data["daily_goal"] > 0
    assert isinstance(data["recent_foods"], list)


@pytest.mark.asyncio
async def test_daily_summary_reflects_logged_food(client):
    await client.post(
        "/api/food/log",
        json={"name": "oats", "calories": 300, "protein_g": 10, "carbs_g": 50, "fat_g": 5},
    )
    resp = await client.get("/api/analytics/daily-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["calories_in"] == 300
    assert data["net_calories"] == 300
    assert data["remaining"] == data["daily_goal"] - 300


@pytest.mark.asyncio
async def test_daily_summary_recent_foods_populated(client):
    await client.post("/api/food/log", json={"name": "banana", "calories": 90})
    resp = await client.get("/api/analytics/daily-summary")
    data = resp.json()
    names = [f["name"] for f in data["recent_foods"]]
    assert "banana" in names


@pytest.mark.asyncio
async def test_daily_summary_recent_foods_deduplicated(client):
    for _ in range(3):
        await client.post("/api/food/log", json={"name": "apple", "calories": 80})
    resp = await client.get("/api/analytics/daily-summary")
    data = resp.json()
    names = [f["name"] for f in data["recent_foods"]]
    assert names.count("apple") == 1
