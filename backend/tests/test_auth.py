import pytest


async def _register(client, email, password="secret123", name="Tester"):
    return await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )


@pytest.mark.asyncio
async def test_register_returns_token_and_user(raw_client):
    res = await _register(raw_client, "alice@example.com")
    assert res.status_code == 201
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email_conflicts(raw_client):
    await _register(raw_client, "dup@example.com")
    res = await _register(raw_client, "dup@example.com")
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_login_succeeds_with_correct_password(raw_client):
    await _register(raw_client, "bob@example.com", password="hunter2")
    res = await raw_client.post(
        "/api/auth/login", json={"email": "bob@example.com", "password": "hunter2"}
    )
    assert res.status_code == 200
    assert res.json()["access_token"]


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(raw_client):
    await _register(raw_client, "carol@example.com", password="rightpass")
    res = await raw_client.post(
        "/api/auth/login", json={"email": "carol@example.com", "password": "wrongpass"}
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_token(raw_client):
    res = await raw_client.get("/api/profile")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(raw_client):
    reg = await _register(raw_client, "dave@example.com")
    token = reg.json()["access_token"]
    res = await raw_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "dave@example.com"


@pytest.mark.asyncio
async def test_food_data_is_isolated_between_users(raw_client):
    # Two registered users
    t1 = (await _register(raw_client, "u1@example.com")).json()["access_token"]
    t2 = (await _register(raw_client, "u2@example.com")).json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}

    # User 1 logs a food entry
    log = await raw_client.post(
        "/api/food/log",
        headers=h1,
        json={"name": "Idli", "calories": 150, "protein_g": 4, "carbs_g": 30, "fat_g": 1},
    )
    assert log.status_code == 201

    # User 1 sees it
    today1 = await raw_client.get("/api/food/today", headers=h1)
    assert len(today1.json()) == 1

    # User 2 sees nothing
    today2 = await raw_client.get("/api/food/today", headers=h2)
    assert today2.json() == []


@pytest.mark.asyncio
async def test_cannot_delete_another_users_entry(raw_client):
    t1 = (await _register(raw_client, "owner@example.com")).json()["access_token"]
    t2 = (await _register(raw_client, "intruder@example.com")).json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}

    log = await raw_client.post(
        "/api/food/log", headers=h1, json={"name": "Dosa", "calories": 200}
    )
    entry_id = log.json()["id"]

    # Intruder cannot delete it
    res = await raw_client.delete(f"/api/food/{entry_id}", headers=h2)
    assert res.status_code == 404

    # Owner still sees it
    today = await raw_client.get("/api/food/today", headers=h1)
    assert len(today.json()) == 1
