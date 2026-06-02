Generate pytest tests for: $ARGUMENTS

Rules:
- Use httpx AsyncClient with ASGITransport (not TestClient)
- Mock external services (gemini_service) with pytest-mock
- Test happy path + at least 2 error cases per route
- Use pytest.mark.asyncio on all tests
- Follow existing test file structure in backend/tests/
- Import the FastAPI app from app.main

Generate the complete test file, ready to run with: pytest backend/tests/
