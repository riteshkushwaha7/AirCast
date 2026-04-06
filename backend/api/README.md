# AirWise Backend (Batch 2 Foundation)

This backend provides a clean, layered FastAPI architecture for AirWise.

## Structure
```text
app/
  main.py
  api/
    deps.py
    router.py
    routes/
  core/
  db/
  models/
  schemas/
  repositories/
  services/
  integrations/
  utils/
migrations/
scripts/
tests/
```

## Domain Coverage
- User
- UserProfile
- SavedLocation
- AlertPreference
- DeviceToken
- ForecastLog
- NotificationLog

## API Endpoints
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/onboarding/complete`
- `GET /api/v1/profile`
- `PUT /api/v1/profile`
- `GET /api/v1/locations`
- `POST /api/v1/locations`
- `PATCH /api/v1/locations/{location_id}`
- `DELETE /api/v1/locations/{location_id}`
- `POST /api/v1/locations/{location_id}/set-primary`
- `GET /api/v1/alerts/preferences`
- `PUT /api/v1/alerts/preferences`
- `POST /api/v1/notifications/device-token`
- `DELETE /api/v1/notifications/device-token/{token_id}`
- `GET /api/v1/aqi/current`
- `GET /api/v1/aqi/current/by-coordinates`
- `GET /api/v1/aqi/history`
- `GET /api/v1/forecasts/current`
- `GET /api/v1/forecasts/weekly`
- `GET /api/v1/forecasts/best-window`
- `POST /api/v1/forecasts/generate-demo`
- `GET /api/v1/recommendations/current`
- `POST /api/v1/assistant/explain`
- `GET /api/v1/admin/health`
- `GET /api/v1/admin/metrics-summary`

## Local Setup
1. Create env file:
```bash
cp .env.example .env
```
2. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```
3. (Optional) Bootstrap schema for local DB:
```bash
psql "$POSTGRES_URI" -f scripts/schema.sql
```
4. Run API:
```bash
uvicorn app.main:app --reload --port 8000
```

## Auth Notes
- Production: verify Firebase JWT with `firebase_admin` in `integrations/firebase_auth.py`.
- Local dev: `ALLOW_MOCK_AUTH=true`, and pass `Authorization: Bearer dev-token`.

## InfluxDB Time-Series Design
Measurement support in `repositories/aqi_timeseries_repository.py`:
- `aqi_raw`
- `aqi_processed`
- `aqi_predictions`
- `model_metrics`
- `pollutant_raw` (stub-ready)

## Next Batch Integration Points
- Real CPCB/OGD ingestion adapters
- LSTM inference service hookup
- Scheduled alert dispatch and best-window jobs
- Assistant integration on structured context only
