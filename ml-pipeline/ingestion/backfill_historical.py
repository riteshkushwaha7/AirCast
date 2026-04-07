import argparse
import json
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path


def bootstrap_paths() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    backend_root = repo_root / "backend" / "api"
    pipeline_root = repo_root / "ml-pipeline"
    for path in (str(backend_root), str(pipeline_root)):
        if path not in sys.path:
            sys.path.insert(0, path)


def parse_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def main() -> None:
    bootstrap_paths()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    from app.db.influx import get_influx_provider
    from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
    from app.services.ingestion_service import IngestionService

    parser = argparse.ArgumentParser(description="Backfill AQI history from OpenAQ-style source")
    parser.add_argument("--city", required=True, help="City name (e.g. Delhi)")
    parser.add_argument("--days", type=int, default=30, help="Number of days to backfill")
    parser.add_argument("--start", default=None, help="Optional ISO start datetime")
    parser.add_argument("--end", default=None, help="Optional ISO end datetime")
    parser.add_argument("--limit", type=int, default=2000, help="Maximum records to fetch")
    args = parser.parse_args()

    start = parse_dt(args.start)
    end = parse_dt(args.end)
    if end is None:
        end = datetime.now(tz=UTC)
    if start is None:
        start = end - timedelta(days=args.days)

    repo = AQITimeSeriesRepository(get_influx_provider())
    service = IngestionService(timeseries_repository=repo)
    summary = service.backfill_from_openaq(city=args.city, days=args.days, start_at=start, end_at=end, limit=args.limit)

    print(json.dumps(summary.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
