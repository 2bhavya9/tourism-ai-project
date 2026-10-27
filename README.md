# Tourism AI Decision Support System

This project is an intelligent tourism analytics and travel planning system built as a final-year AI and Data Science project.

## Features
- AI-based destination recommendations
- Tourism dashboard with summary metrics and charts
- Personalized travel plans
- Budget estimator
- Destination comparison
- Explainable recommendation reasons
- Rule-based chat assistant fallback

## Tech stack
- Frontend: React + Vite
- Backend: Python + FastAPI
- ML/data processing: pandas, numpy, scikit-learn
- Data: JSON sample dataset

## Running backend
```bash
cd tourism-ai-project
. .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running frontend
```bash
cd tourism-ai-project/frontend
npm install
npm run dev -- --host 0.0.0.0
```

For a hosted frontend, set `VITE_API_BASE_URL` to the deployed backend URL before building. Local Vite development proxies `/api` requests to `http://localhost:8000`.

## API examples
- GET /api/health
- GET /api/destinations
- POST /api/recommendations
- POST /api/travel-plan
- POST /api/budget/estimate
- GET /api/analytics/dashboard
- POST /api/chat

## Notes
This project uses sample/demo data and is designed for academic demonstration.
