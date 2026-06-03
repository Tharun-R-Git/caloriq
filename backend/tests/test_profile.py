import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db import get_db, Base
from tests.conftest import TestSession, engine


# ---------------------------------------------------------------------------
# Shared payload fixtures
# ---------------------------------------------------------------------------

FULL_SETUP = {
    "name": "Alex",
    "email": "alex@example.com",
    "age": 28,
    "gender": "male",
    "height_cm": 175.0,
    "weight_kg": 75.0,
    "activity_level": "moderate",
    "aim": "maintain",
}


async def _setup(client: AsyncClient, payload: dict = None) -> dict:
    resp = await client.post("/api/profile/setup", json=payload or FULL_SETUP)
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# GET /api/profile  — fresh DB, no existing user
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_profile_creates_user_on_first_call(client):
    resp = await client.get("/api/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] is not None
    assert data["is_setup"] is False
    assert data["goals"] is None


@pytest.mark.asyncio
async def test_get_profile_returns_same_user_on_repeated_calls(client):
    r1 = await client.get("/api/profile")
    r2 = await client.get("/api/profile")
    assert r1.json()["id"] == r2.json()["id"]


@pytest.mark.asyncio
async def test_get_profile_after_setup_is_setup_true(client):
    await _setup(client)
    resp = await client.get("/api/profile")
    assert resp.status_code == 200
    assert resp.json()["is_setup"] is True


# ---------------------------------------------------------------------------
# POST /api/profile/setup — happy path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_setup_profile_happy_path(client):
    resp = await client.post("/api/profile/setup", json=FULL_SETUP)
    assert resp.status_code == 200
    data = resp.json()

    assert data["name"] == "Alex"
    # email is the login identity (owned by auth); profile setup must not change it
    assert data["email"] == "test@example.com"
    assert data["age"] == 28
    assert data["gender"] == "male"
    assert data["height_cm"] == 175.0
    assert data["weight_kg"] == 75.0
    assert data["activity_level"] == "moderate"
    assert data["aim"] == "maintain"
    assert data["is_setup"] is True


@pytest.mark.asyncio
async def test_setup_profile_returns_calculated_goals(client):
    resp = await client.post("/api/profile/setup", json=FULL_SETUP)
    goals = resp.json()["goals"]

    assert goals is not None
    assert goals["bmr"] > 0
    assert goals["tdee"] > goals["bmr"]
    assert goals["daily_goal"] > 0
    assert goals["protein_goal_g"] > 0
    assert goals["carbs_goal_g"] > 0
    assert goals["fat_goal_g"] > 0


@pytest.mark.asyncio
async def test_setup_profile_goal_calories_cached(client):
    resp = await client.post("/api/profile/setup", json=FULL_SETUP)
    data = resp.json()
    assert data["goal_calories"] == data["goals"]["daily_goal"]


@pytest.mark.asyncio
async def test_setup_profile_female_bmr_different_from_male(client):
    male_resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "gender": "male"})
    female_resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "gender": "female"})
    assert male_resp.json()["goals"]["bmr"] != female_resp.json()["goals"]["bmr"]


@pytest.mark.asyncio
async def test_setup_profile_lose_aim_lowers_goal(client):
    maintain = await client.post("/api/profile/setup", json={**FULL_SETUP, "aim": "maintain"})
    lose = await client.post("/api/profile/setup", json={**FULL_SETUP, "aim": "lose"})
    assert lose.json()["goals"]["daily_goal"] == maintain.json()["goals"]["daily_goal"] - 500


@pytest.mark.asyncio
async def test_setup_profile_gain_aim_raises_goal(client):
    maintain = await client.post("/api/profile/setup", json={**FULL_SETUP, "aim": "maintain"})
    gain = await client.post("/api/profile/setup", json={**FULL_SETUP, "aim": "gain"})
    assert gain.json()["goals"]["daily_goal"] == maintain.json()["goals"]["daily_goal"] + 300


@pytest.mark.asyncio
async def test_setup_profile_idempotent_upsert(client):
    await _setup(client)
    resp2 = await client.post("/api/profile/setup", json={**FULL_SETUP, "name": "Alex V2"})
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Alex V2"
    # Still only one user in the system
    get_resp = await client.get("/api/profile")
    assert get_resp.json()["name"] == "Alex V2"


# ---------------------------------------------------------------------------
# POST /api/profile/setup — validation errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_setup_profile_missing_required_field(client):
    payload = {k: v for k, v in FULL_SETUP.items() if k != "age"}
    resp = await client.post("/api/profile/setup", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_age_below_minimum(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "age": 5})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_age_above_maximum(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "age": 150})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_invalid_gender(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "gender": "robot"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_invalid_activity_level(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "activity_level": "extreme"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_invalid_aim(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "aim": "shred"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_height_below_minimum(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "height_cm": 50.0})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_setup_profile_weight_below_minimum(client):
    resp = await client.post("/api/profile/setup", json={**FULL_SETUP, "weight_kg": 5.0})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/profile/goals
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_goals_before_setup_returns_defaults(client):
    resp = await client.get("/api/profile/goals")
    assert resp.status_code == 200
    data = resp.json()
    assert data["daily_goal"] == 2000
    assert data["bmr"] == 0.0
    assert data["tdee"] == 0.0


@pytest.mark.asyncio
async def test_get_goals_after_setup_returns_real_values(client):
    await _setup(client)
    resp = await client.get("/api/profile/goals")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bmr"] > 0
    assert data["tdee"] > 0
    assert data["daily_goal"] > 0
    assert set(data.keys()) == {"bmr", "tdee", "daily_goal", "protein_goal_g", "carbs_goal_g", "fat_goal_g"}


@pytest.mark.asyncio
async def test_get_goals_macro_split_sums_to_roughly_daily_goal(client):
    await _setup(client)
    data = (await client.get("/api/profile/goals")).json()
    # protein 30% @4, carbs 45% @4, fat 25% @9 — should approximately reconstruct daily_goal
    reconstructed = (
        data["protein_goal_g"] * 4
        + data["carbs_goal_g"] * 4
        + data["fat_goal_g"] * 9
    )
    assert abs(reconstructed - data["daily_goal"]) < 50  # rounding tolerance


# ---------------------------------------------------------------------------
# PUT /api/profile  — partial updates
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_put_profile_partial_update(client):
    await _setup(client)
    resp = await client.put("/api/profile", json={"name": "Alex Updated", "weight_kg": 80.0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Alex Updated"
    assert data["weight_kg"] == 80.0
    assert data["age"] == 28  # unchanged


@pytest.mark.asyncio
async def test_put_profile_recalculates_goal_on_weight_change(client):
    await _setup(client)
    before = (await client.get("/api/profile/goals")).json()["daily_goal"]
    await client.put("/api/profile", json={"weight_kg": 100.0})
    after = (await client.get("/api/profile/goals")).json()["daily_goal"]
    assert after != before


@pytest.mark.asyncio
async def test_put_profile_invalid_gender_rejected(client):
    await _setup(client)
    resp = await client.put("/api/profile", json={"gender": "unknown"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_invalid_activity_level_rejected(client):
    await _setup(client)
    resp = await client.put("/api/profile", json={"activity_level": "turbo"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_invalid_aim_rejected(client):
    await _setup(client)
    resp = await client.put("/api/profile", json={"aim": "bulk"})
    assert resp.status_code == 422
