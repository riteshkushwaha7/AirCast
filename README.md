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
- ML pipeline: Python scripts for ingestion, preprocessing, feature generation, planner projection hooks
- Infra: Docker, Docker Compose

## Repository Structure

```text
backend/
  api/
frontend/
  web/
  mobile/
ml-pipeline/
docs/
seed/
scripts/
docker-compose.yml
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
cp backend/api/.env.example backend/api/.env
```

## Run with Docker (Recommended Demo Path)

```bash
docker compose up --build
```

Services:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- InfluxDB: `http://localhost:8086`
- PostgreSQL: `localhost:5432`

Health check helper:

```bash
python scripts/check_system_health.py
```

Optional shortcuts:

```bash
make dev
make seed
make health
```

## Local Run (Without Docker)

Backend:
```bash
cd backend/api
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

ML pipeline:
```bash
cd ml-pipeline
pip install -r requirements.txt
python ingestion/run_ingestion.py --city Delhi --limit 100
python preprocessing/clean_timeseries.py --city Delhi --lookback-hours 336
python forecasting/weekly_forecast.py --days 7
```

## Demo / Mock Mode

Use these values for stable demo behavior:

- `ALLOW_MOCK_AUTH=true`
- `SOURCE_MOCK_MODE=true`
- `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true`
- `EXPO_PUBLIC_ENABLE_MOCK_FALLBACK=true`

Seed demo data:
```bash
python scripts/seed_demo_data.py
```

Demo startup shortcut:
```bash
bash scripts/run_demo_mode.sh
# or PowerShell:
powershell -ExecutionPolicy Bypass -File scripts/run_demo_mode.ps1
```

## Sample Demo Flow

1. Open landing page (`/`)
2. Log in with demo auth mode
3. Show onboarding/profile setup
4. Show dashboard AQI + short-horizon forecast
5. Show recommendation + alert preferences
6. Open weekly planner and highlight best/caution days
7. Mention backend route coverage and data stores
8. Mention ML ingestion/preprocessing + planner projection hooks

Detailed presenter script: [docs/demo-script.md](docs/demo-script.md)

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
