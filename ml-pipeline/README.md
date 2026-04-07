# AirWise ML/Data Pipeline

This folder contains the AQI ingestion and preprocessing pipeline layer for AirWise.

It is structured to support future model training, retraining, inference, and analytics while staying runnable in mock mode.

## Structure
```text
ml-pipeline/
  ingestion/
    run_ingestion.py
    backfill_historical.py
  preprocessing/
    clean_timeseries.py
    resample_series.py
    generate_features.py
  datasets/
    build_training_dataset.py
  shared/
    schemas.py
    constants.py
    time_utils.py
    category_utils.py
    validation_utils.py
  tests/
    fixtures/
```

## What This Batch Adds
- source-aware ingestion entry points
- OpenAQ-style historical backfill runner
- normalized AQI schema and validation helpers
- deduplication helpers
- hourly resampling with missing/imputed flags
- feature generation for rolling/lag/temporal predictors
- dataset builder hooks for train/validation/test and sequence windows

## Prerequisites
- backend API dependencies installed (for shared backend service imports)
- InfluxDB running for real writes
- `.env` in `backend/api` configured (or use mock mode)

Install dependencies:
```bash
cd ml-pipeline
pip install -r requirements.txt
```

## CLI Usage

### Current ingestion (CPCB-style)
```bash
python ingestion/run_ingestion.py --city Delhi --limit 500
```

### Historical backfill (OpenAQ-style)
```bash
python ingestion/backfill_historical.py --city Delhi --days 30
```

### Preprocessing run from InfluxDB raw series
```bash
python preprocessing/clean_timeseries.py --city Delhi --lookback-hours 336
```

### CSV resampling utility
```bash
python preprocessing/resample_series.py --input data/raw/aqi_backfill.csv --output data/processed/aqi_resampled.csv
```

### CSV feature generation utility
```bash
python preprocessing/generate_features.py --input data/processed/aqi_resampled.csv --output data/processed/aqi_features.csv
```

### Build training dataset from processed InfluxDB series
```bash
python datasets/build_training_dataset.py --city Delhi --out data/processed/training_dataset.csv
```

## Testing
```bash
pytest tests -q
```

Coverage includes:
- timestamp parsing/normalization
- category mapping
- validation and deduplication logic
- missing/imputed behavior in resampling

## Notes
- The pipeline is adapter-driven and mockable; it is safe for local demos without live external credentials.
- Weather enrichment is intentionally deferred to a later batch and represented by backend stubs.
- LSTM training is not implemented here, but the output schema and sequence hooks are prepared for it.
