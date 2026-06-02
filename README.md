# CaloriQ

A mobile-first calorie tracking web app with AI-powered meal analysis.

## Stack
- **Frontend**: React 18 + Vite + Tailwind CSS + Recharts
- **Backend**: FastAPI + SQLAlchemy (async) + SQLite + Gemini AI

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # add your GEMINI_API_KEY
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173  
API: http://localhost:8000  
API docs: http://localhost:8000/docs
