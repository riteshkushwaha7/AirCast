# AirWise

AirWise is a personalized AQI forecasting and alert platform prototype for web and mobile.  
It helps users understand current and upcoming air quality in simple terms, with profile-aware recommendations and weekly planning support.

## Key Features

- Current AQI + 4h/6h/12h/24h forecast summaries
- Personalized recommendation logic (health profile, sensitivity, activity)
- Alert preference system + notification delivery stubs
- 7-day planner with daily summaries, best-day highlights, and activity suitability
- Ingestion and preprocessing pipeline for time-series AQI data
- Mock/demo mode for stable presentations without live providers

## Tech Stack

- Web: Next.js (App Router), TypeScript, Tailwind CSS
- Mobile: React Native (Expo), TypeScript, NativeWind
- Backend: FastAPI, SQLAlchemy, Pydantic
- Data: PostgreSQL (relational), InfluxDB (time-series)
- Notifications: Firebase Cloud Messaging wrapper (mock/dry-run ready)
- Data utilities live inside the backend service (ingestion, preprocessing, forecasting helpers)
- Render deployment (no Docker required)

## Repository Structure

```text
backend/
frontend/
shared/
docs/
```

## Environment Setup

1. Copy root env:
```bash
cp .env.example .env
```

2. Copy client envs:
```bash
cp frontend/web/.env.local.example frontend/web/.env.local
cp frontend/mobile/.env.example frontend/mobile/.env
cp backend/.env.example backend/.env
```

## Local Run (Without Docker)

Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Web:
```bash
cd frontend/web
npm install
npm run dev
```

Mobile:
```bash
cd frontend/mobile
npm install
npm run start
```

## Sample Demo Flow

1. Open landing page (`/`)
2. Log in with demo auth mode
3. Show onboarding/profile setup
4. Show dashboard AQI + short-horizon forecast
5. Show recommendation + alert preferences
6. Open weekly planner and highlight best/caution days
7. Mention backend route coverage and data stores

## Screenshots

Add screenshots/gifs here before final submission:

- `docs/assets/landing.png`
- `docs/assets/dashboard.png`
- `docs/assets/planner.png`
- `docs/assets/mobile-planner.png`

## Future Scope

- Live CPCB/OGD production ingestion credentials
- Model-based multi-step forecast serving
- Scheduled jobs for daily/weekly summary pushes
- Rich analytics and historical trend comparisons

## Contributor Notes

- Keep business logic in services/domain modules (not route handlers)
- Keep mock fallback available for demo resilience
- Prefer small, focused PR-style changes over broad refactors
