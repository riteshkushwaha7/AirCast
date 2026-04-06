# System Architecture - My AirCast

## High-Level Flow
1. AQI ingestion jobs collect city-level readings from CPCB/OGD-style feeds.
2. Raw observations are written to InfluxDB measurement `aqi_readings`.
3. Preprocessing normalizes and enriches time-series features for model training.
4. LSTM model produces multi-horizon forecasts (4h, 6h, 12h, 24h).
5. Rules engine combines forecast + user health profile to generate recommendations.
6. Alert engine evaluates user preferences and pushes notifications via FCM.
7. Frontend consumes REST APIs and renders calm, actionable guidance.

## Service Boundaries
- Frontend (`frontend/web`): presentation, onboarding, preferences, dashboard, assistant UI.
- Backend API (`backend/api`): auth integration, profile/location management, forecast/alerts API.
- ML pipeline (`ml-pipeline`): ingestion, training, evaluation, inference artifacts, retraining schedule.
- Datastores:
  - PostgreSQL: user/profile/settings/locations/preferences/device tokens
  - InfluxDB: AQI sensor time-series (city-level and station-level expansion-ready)

## Time-Series Storage Design (InfluxDB)
- Bucket: `aqi_raw`
- Measurement: `aqi_readings`
- Tags:
  - `city` (e.g., `new delhi`)
  - `station_id` (optional future)
  - `source` (e.g., `cpcb`, `openaq_backfill`)
- Fields:
  - `aqi` (float)
  - `pm25` (optional future)
  - `pm10` (optional future)
- Timestamp:
  - UTC event time from source feed

Retention + downsampling strategy:
- Hot retention: 90 days raw points.
- Warm retention: 12 months hourly aggregates (continuous tasks).
- Long-term archive: object storage export by day.

## Personalization Logic
Input dimensions:
- AQI category
- health profile
- sensitivity level
- optional activity type

Output dimensions:
- one-line recommendation
- mask recommendation boolean
- avoid-outdoor boolean
- best outdoor window string

## LLM Assistant Constraint
Assistant consumes only structured API payloads (`/assistant/context`) and cannot perform AQI prediction.
