# AirWise System Architecture

## High-Level View

```text
Web (Next.js) / Mobile (Expo)
            |
            v
      FastAPI Backend
   (auth, profile, forecast,
 recommendation, alerts, planner)
      |                    |
      v                    v
 PostgreSQL            InfluxDB
 (users/settings)      (AQI time-series)
            ^
            |
      ML/Data Pipeline
 (ingestion, preprocessing,
 feature generation, planner projection hooks)
```

## Frontend/Backend Flow

- Web/mobile call REST endpoints under `/api/v1`
- Backend applies user/profile/location context
- Services convert AQI + forecast data into recommendations and planner summaries
- Responses are optimized for simple UI rendering (badges, short hints, booleans)

## PostgreSQL Usage

Stores:

- users
- profiles
- saved locations
- alert preferences
- device tokens
- forecast and notification logs

## InfluxDB Usage

Stores AQI time-series measurements:

- `aqi_raw`
- `aqi_processed`
- `aqi_predictions`
- `model_metrics`

## Forecast + Planner Flow

1. AQI data ingested and normalized
2. Processed series generated (resampling + features)
3. Forecast service provides near-term outputs
4. Planner service creates 7-day daily summaries with confidence labels and best windows

## Notification Flow

1. Alert engine evaluates thresholds/trends/recommendation state
2. Notification service resolves active tokens
3. FCM wrapper sends (or dry-runs) payloads
4. Notification logs are persisted for traceability

## Deployment View (Local)

- Docker Compose:
  - `postgres`
  - `influxdb`
  - `api`
  - `web`
  - optional `ml-pipeline` profile
