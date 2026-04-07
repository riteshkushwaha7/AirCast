import argparse
import json
import logging
import sys
from pathlib import Path


def bootstrap_paths() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    backend_root = repo_root / "backend" / "api"
    pipeline_root = repo_root / "ml-pipeline"
    for path in (str(backend_root), str(pipeline_root)):
        if path not in sys.path:
            sys.path.insert(0, path)


def main() -> None:
    bootstrap_paths()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    from app.db.influx import get_influx_provider
    from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
    from app.services.preprocessing_service import PreprocessingService

    parser = argparse.ArgumentParser(description="Run raw AQI preprocessing and feature generation")
    parser.add_argument("--city", default=None, help="Optional city filter")
    parser.add_argument("--station-id", default=None, help="Optional station ID filter")
    parser.add_argument("--lookback-hours", type=int, default=336, help="How many hours of raw data to process")
    args = parser.parse_args()

    repo = AQITimeSeriesRepository(get_influx_provider())
    service = PreprocessingService(timeseries_repository=repo)
    summary = service.run_preprocessing(city=args.city, station_id=args.station_id, lookback_hours=args.lookback_hours)

    print(json.dumps(summary.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
