# AirWise Backend (FastAPI)

Production-style backend foundation for AQI forecasting, recommendations, alerts, and weekly planning.

## What It Includes

- Auth integration wrapper (Firebase token verification + mock auth mode)
- User/profile/location domains on PostgreSQL
- AQI/forecast/recommendation/alert/planner APIs
- Notification token + dispatch flow with FCM dry-run support
- InfluxDB repository hooks for raw/processed/prediction time-series
- Ingestion and preprocessing admin routes

## Main API Groups

- `/api/v1/users`
- `/api/v1/profile`
- `/api/v1/locations`
- `/api/v1/aqi`
- `/api/v1/forecasts`
- `/api/v1/recommendations`
- `/api/v1/alerts`
- `/api/v1/notifications`
- `/api/v1/planner`
- `/api/v1/admin`

## Planner Endpoints

- `GET /api/v1/planner/weekly`
- `GET /api/v1/planner/best-days`
- `GET /api/v1/planner/activity?activity_type=running`
- `POST /api/v1/planner/generate-demo`

## Local Setup

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Docs:

- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/admin/health`

## Test

```bash
pytest tests -q
```
