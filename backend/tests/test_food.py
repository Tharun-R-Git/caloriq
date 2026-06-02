import base64
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

MOCK_PHOTO_ANALYSIS = {
    "calories": 320,
    "protein_g": 18.0,
    "carbs_g": 40.0,
    "fat_g": 9.0,
    "food_name": "Grilled chicken with rice",
    "serving_size": "1 plate (300g)",
    "confidence": 0.87,
    "items_detected": ["grilled chicken", "white rice", "salad"],
}

# minimal valid base64 payload — service is mocked so actual bytes don't matter
_FAKE_IMAGE_B64 = base64.b64encode(b"fake-image-bytes").decode()


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
async def test_analyze_food_with_description(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food",
        new_callable=AsyncMock,
        return_value=MOCK_ANALYSIS,
    ) as mock_analyze:
        resp = await client.post(
            "/api/food/analyze",
            json={"name": "chicken biryani", "description": "homemade, extra oil"},
        )
    assert resp.status_code == 200
    mock_analyze.assert_awaited_once_with("chicken biryani", "homemade, extra oil")


@pytest.mark.asyncio
async def test_analyze_food_missing_name(client):
    resp = await client.post("/api/food/analyze", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_food_gemini_failure_returns_mock(client):
    # Mock the internal sync call so the service's own try/except fallback fires
    with patch(
        "app.services.gemini_service.GeminiService._call_mistral",
        side_effect=Exception("quota exceeded"),
    ):
        resp = await client.post("/api/food/analyze", json={"name": "pizza"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["calories"] > 0


# ---------------------------------------------------------------------------
# POST /api/food/analyze-photo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_analyze_photo_happy_path_jpeg(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food_photo",
        new_callable=AsyncMock,
        return_value=MOCK_PHOTO_ANALYSIS,
    ):
        resp = await client.post(
            "/api/food/analyze-photo",
            json={"image_base64": _FAKE_IMAGE_B64, "mime_type": "image/jpeg"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["calories"] == 320
    assert data["food_name"] == "Grilled chicken with rice"
    assert data["items_detected"] == ["grilled chicken", "white rice", "salad"]
    assert "confidence" in data


@pytest.mark.asyncio
async def test_analyze_photo_happy_path_png(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food_photo",
        new_callable=AsyncMock,
        return_value=MOCK_PHOTO_ANALYSIS,
    ):
        resp = await client.post(
            "/api/food/analyze-photo",
            json={"image_base64": _FAKE_IMAGE_B64, "mime_type": "image/png"},
        )
    assert resp.status_code == 200
    assert resp.json()["calories"] == 320


@pytest.mark.asyncio
async def test_analyze_photo_invalid_mime_type(client):
    resp = await client.post(
        "/api/food/analyze-photo",
        json={"image_base64": _FAKE_IMAGE_B64, "mime_type": "image/gif"},
    )
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert any("mime_type" in str(d) for d in detail)


@pytest.mark.asyncio
async def test_analyze_photo_missing_image_base64(client):
    resp = await client.post(
        "/api/food/analyze-photo",
        json={"mime_type": "image/jpeg"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_photo_missing_mime_type(client):
    resp = await client.post(
        "/api/food/analyze-photo",
        json={"image_base64": _FAKE_IMAGE_B64},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_photo_oversized_image(client):
    # 14_000_001 chars exceeds the validator limit (~10 MB)
    oversized = "A" * 14_000_001
    resp = await client.post(
        "/api/food/analyze-photo",
        json={"image_base64": oversized, "mime_type": "image/jpeg"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_photo_passes_correct_args_to_service(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food_photo",
        new_callable=AsyncMock,
        return_value=MOCK_PHOTO_ANALYSIS,
    ) as mock_fn:
        await client.post(
            "/api/food/analyze-photo",
            json={"image_base64": _FAKE_IMAGE_B64, "mime_type": "image/jpeg"},
        )
    mock_fn.assert_awaited_once_with(_FAKE_IMAGE_B64, "image/jpeg")


@pytest.mark.asyncio
async def test_analyze_photo_response_schema(client):
    with patch(
        "app.routes.food.GeminiService.analyze_food_photo",
        new_callable=AsyncMock,
        return_value=MOCK_PHOTO_ANALYSIS,
    ):
        resp = await client.post(
            "/api/food/analyze-photo",
            json={"image_base64": _FAKE_IMAGE_B64, "mime_type": "image/jpeg"},
        )
    data = resp.json()
    for field in ("calories", "protein_g", "carbs_g", "fat_g", "food_name", "serving_size", "confidence", "items_detected"):
        assert field in data, f"Missing field: {field}"
    assert isinstance(data["items_detected"], list)


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


@pytest.mark.asyncio
async def test_log_food_optional_fields_default(client):
    resp = await client.post("/api/food/log", json={"name": "dosa", "calories": 150})
    assert resp.status_code == 201
    data = resp.json()
    assert data["protein_g"] == 0
    assert data["carbs_g"] == 0
    assert data["fat_g"] == 0


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


@pytest.mark.asyncio
async def test_get_today_returns_multiple_entries(client):
    await client.post("/api/food/log", json={"name": "idli", "calories": 80})
    await client.post("/api/food/log", json={"name": "sambar", "calories": 60})
    resp = await client.get("/api/food/today")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ---------------------------------------------------------------------------
# GET /api/food/history
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_history_empty(client):
    resp = await client.get("/api/food/history")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_history_groups_by_date(client):
    await client.post("/api/food/log", json={"name": "upma", "calories": 200})
    resp = await client.get("/api/food/history")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert "date" in data[0]
    assert "entries" in data[0]
    assert "total_calories" in data[0]
    assert data[0]["total_calories"] == 200.0


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


@pytest.mark.asyncio
async def test_delete_wrong_type_id(client):
    resp = await client.delete("/api/food/not-an-int")
    assert resp.status_code == 422
