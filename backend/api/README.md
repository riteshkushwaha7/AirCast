# AirWise Backend API

Production-style FastAPI backend foundation for AirWise.

This batch extends the project with AQI data ingestion and preprocessing services designed for:
- current AQI retrieval
- historical backfill
- time-series preprocessing
- feature generation for future LSTM training

## Structure
```text
app/
  api/
    routes/
      admin.py
  core/
  db/
  integrations/
    cpcb_client.py
    openaq_client.py
    weather_client.py
  repositories/
    aqi_timeseries_repository.py
  schemas/
    ingestion.py
  services/
    ingestion_service.py
    preprocessing_service.py
    feature_service.py
    dataset_service.py
```

## Key Ingestion/Processing Endpoints
- `POST /api/v1/admin/ingestion/run-current`
- `POST /api/v1/admin/ingestion/backfill`
- `POST /api/v1/admin/preprocessing/run`
- `GET /api/v1/admin/ingestion/summary`
- `POST /api/v1/admin/datasets/build`

Existing core endpoints for users/profile/locations/alerts/aqi/forecasts stay unchanged.

## InfluxDB Measurement Design

### `aqi_raw`
Tags:
- `source`
- `station_id`
- `city`
- `state`
- `country`

Fields:
- `aqi`
- `pm25`, `pm10`, `no2`, `so2`, `co`, `o3`, `nh3`
- `latitude`, `longitude`

Timestamp:
- `observed_at`

### `aqi_processed`
Tags:
- `source`
- `station_id`
- `city`

Fields:
- `aqi`
- `rolling_avg_3h`, `rolling_avg_6h`, `rolling_avg_12h`
- `lag_1`, `lag_3`, `lag_6`, `lag_12`, `lag_24`
- `hour_of_day`, `day_of_week`, `is_weekend`
- `missing_flag`, `imputed_flag`

Timestamp:
- `observed_at`

## Local Setup
1. Copy env:
```bash
cp .env.example .env
```
2. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```
3. Run API:
```bash
uvicorn app.main:app --reload --port 8000
```

## Pipeline Behavior Notes
- Source clients support `SOURCE_MOCK_MODE=true` so ingestion is runnable without live credentials.
- Ingestion validates and normalizes to `NormalizedAQIRecord`.
- Deduplication key:
  - primary: `source + station_id + observed_at`
  - fallback: `source + city + lat + lon + observed_at`
- Preprocessing includes:
  - hourly resampling
  - short-gap conservative imputation
  - missing/imputed flags
  - rolling and lag features

## Tests
```bash
pytest tests -q
```

Includes tests for validation, normalization, dedupe, feature generation, and preprocessing missing-value behavior.
