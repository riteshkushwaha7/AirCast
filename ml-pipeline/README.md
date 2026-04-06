# ML Pipeline - My AirCast

This folder provides a production-oriented skeleton for AQI forecasting with LSTM.

## Modules
- `src/data`: ingestion and preprocessing scripts
- `src/features`: feature engineering utilities
- `src/models`: training, evaluation, and model registry logic
- `src/inference`: runtime prediction helpers
- `src/retrain`: scheduled retraining hooks

## Commands
```bash
python -m src.data.ingest_cpcb --city "New Delhi"
python -m src.data.backfill_openaq --city "New Delhi"
python -m src.data.preprocess --input data/raw/aqi_sample.csv --output data/processed/aqi_processed.csv
python -m src.models.train_lstm --config config/train_config.yaml
python -m src.models.evaluate --model models/registry/latest
python -m src.inference.predict --model models/registry/latest --aqi-seq "142,138,150,160,171"
python -m src.retrain.schedule --config config/train_config.yaml
```

## Notes
- This skeleton expects real AQI ingestion to be connected to CPCB/OGD feed connectors.
- OpenAQ-style harmonized historical data can be used for backfill.
- 7-day outlook is generated as a daily summary post-processing layer from model and trend heuristics.
