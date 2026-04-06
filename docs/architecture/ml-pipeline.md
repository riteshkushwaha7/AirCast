# ML Pipeline Structure

## Data Inputs
- Real-time AQI feed: CPCB/OGD-style connectors
- Historical backfill: OpenAQ-like harmonized exports

## Stages
1. `src/data/ingest_cpcb.py` - pull latest readings
2. `src/data/backfill_openaq.py` - historical fill
3. `src/data/preprocess.py` - clean, normalize, rolling stats
4. `src/features/build_features.py` - sequences and temporal features
5. `src/models/train_lstm.py` - train/val/test split and model fit
6. `src/models/evaluate.py` - evaluate on sample sequences
7. `src/models/registry.py` - register model metadata + artifacts
8. `src/inference/predict.py` - produce 4h/6h/12h/24h + daily summary adapter
9. `src/retrain/schedule.py` - periodic retraining trigger

## Core Features Used
- Past AQI values
- Rolling averages (3, 12)
- Hour-of-day
- Day-of-week

## Outputs
- Horizon forecasts: 4h, 6h, 12h, 24h
- 7-day planning summary (post-processing)
- Registry artifact with metrics and model metadata
