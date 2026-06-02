import pytest


@pytest.mark.asyncio
async def test_trends_returns_correct_shape(client):
    resp = await client.get("/api/analytics/trends?days=7")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 7
    for day in data:
        assert "date" in day
        assert "calories_in" in day
        assert "calories_burned" in day
        assert "net" in day
        assert "protein_g" in day
        assert "carbs_g" in day
        assert "fat_g" in day
        assert "goal" in day


@pytest.mark.asyncio
async def test_trends_zeros_for_empty_days(client):
    resp = await client.get("/api/analytics/trends?days=3")
    data = resp.json()
    for day in data:
        assert day["calories_in"] == 0.0
        assert day["calories_burned"] == 0.0
        assert day["net"] == 0.0


@pytest.mark.asyncio
async def test_trends_reflects_logged_food(client):
    await client.post("/api/food/log", json={"name": "rice", "calories": 400, "protein_g": 8, "carbs_g": 80, "fat_g": 2})
    resp = await client.get("/api/analytics/trends?days=1")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["calories_in"] == 400.0
    assert data[0]["protein_g"] == 8.0
    assert data[0]["carbs_g"] == 80.0
    assert data[0]["net"] == 400.0


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
