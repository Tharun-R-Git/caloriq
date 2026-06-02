# CaloriQ — CLAUDE.md

## Project overview

CaloriQ is a personal calorie tracking web app. Mobile-first (max-w-md mx-auto on every page).

- **Frontend**: React 18 + Vite, port 5173 (`frontend/`)
- **Backend**: FastAPI + async SQLAlchemy + SQLite (aiosqlite), port 8000 (`backend/`)
- **AI**: Gemini 1.5 Flash for food calorie lookup and (Phase 6) photo analysis
- **DB file**: `backend/caloriq.db` — never commit this

---

## Architecture rules — never violate

- Frontend talks to the backend **only** via `frontend/src/api/api.js`. No `fetch` or `axios` calls anywhere else in the frontend.
- All backend business logic goes in `app/services/`. Routes only handle HTTP concerns (parse request, call service, return response).
- Never put business logic in routes or models.
- All new SQLAlchemy models need a matching Pydantic schema in `app/schemas/`.
- `GEMINI_API_KEY` lives in `backend/.env` only — never hardcode it anywhere.
- `backend/caloriq.db` is gitignored — never commit it.

---

## Calorie math — use these formulas, always

### BMR (Harris-Benedict revised)

```
Men:   88.36  + (13.4  × weight_kg) + (5.0 × height_cm) - (5.7 × age)
Women: 447.6  + (9.25  × weight_kg) + (3.1 × height_cm) - (4.3 × age)
```

### TDEE

```
TDEE = BMR × activity_multiplier

sedentary  → 1.2
light      → 1.375
moderate   → 1.55
active     → 1.725
very_active→ 1.9
```

### Exercise calorie burn

```
calories_burned = MET × weight_kg × duration_hours
```

### Net calories

```
net = food_calories_in - exercise_calories_burned
```

### Daily goal (adjusted for aim)

```
lose:     TDEE - 500
maintain: TDEE
gain:     TDEE + 300
```

All of the above lives in `app/services/calorie_engine.py`. Do not reimplement these formulas elsewhere.

---

## Gemini usage

- **Model**: `gemini-1.5-flash` (free tier)
- **Used for**: food calorie lookup by name/description; photo analysis (Phase 6)
- **All Gemini calls** go through `app/services/gemini_service.py` — nowhere else
- **Always request JSON** from Gemini using this schema:

```json
{
  "calories": 350,
  "protein_g": 12.5,
  "carbs_g": 45.0,
  "fat_g": 8.0,
  "serving_size": "1 cup (240g)",
  "confidence": 0.92
}
```

- Prompt must instruct the model: *"Return only valid JSON, no markdown, no explanation."*
- Validate the response with a Pydantic model before using it.

---

## Frontend rules

- **Tailwind only** — no custom CSS files (the single `src/index.css` for `@tailwind` directives is fine)
- Every page component uses `max-w-md mx-auto px-4` for mobile centering
- API calls only through `src/api/api.js`
- **Recharts** for all charts — no other charting library
- Hooks live in `src/hooks/`, reusable UI in `src/components/`, route-level pages in `src/pages/`

---

## Testing

- **Backend**: `pytest` with `httpx.AsyncClient` against the real async app
- **Frontend**: no tests required until Phase 5
- Every new route must have at least one pytest test in `backend/tests/`

---

## Current status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Scaffold — FastAPI + React + SQLite running | ✅ Complete |
| 2 | Food logger + Gemini integration | 🔄 In progress |
| 3 | Exercise logger + calorie math | ⬜ Not started |
| 4 | Dashboard + analytics | ⬜ Not started |
| 5 | Trends charts + history | ⬜ Not started |
| 6 | Photo analysis (Gemini vision) | ⬜ Not started |

**Gemini API key**: not yet configured — add `GEMINI_API_KEY=...` to `backend/.env`.
