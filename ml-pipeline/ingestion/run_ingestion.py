import argparse
import json
import logging
import sys
from pathlib import Path


def bootstrap_paths() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    backend_root = repo_root / "backend" / "api"
    pipeline_root = repo_root / "ml-pipeline"
    for path in (str(backend_root), str(pipeline_root)):
        if path not in sys.path:
            sys.path.insert(0, path)
    return repo_root


def main() -> None:
    bootstrap_paths()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    from app.db.influx import get_influx_provider
    from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
    from app.services.ingestion_service import IngestionService

    parser = argparse.ArgumentParser(description="Run current AQI ingestion from CPCB-style source")
    parser.add_argument("--city", default=None, help="Optional city filter (e.g. Delhi)")
    parser.add_argument("--limit", type=int, default=500, help="Maximum records to fetch")
    args = parser.parse_args()

    repo = AQITimeSeriesRepository(get_influx_provider())
    service = IngestionService(timeseries_repository=repo)
    summary = service.ingest_current_from_cpcb(city=args.city, limit=args.limit)

    print(json.dumps(summary.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
