import argparse
import json
import sys
from datetime import UTC, datetime
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

    from app.db.influx import get_influx_provider
    from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
    from app.services.dataset_service import DatasetService

    parser = argparse.ArgumentParser(description="Build training dataset from processed AQI series")
    parser.add_argument("--city", default=None, help="City dataset selector")
    parser.add_argument("--station-id", default=None, help="Station dataset selector")
    parser.add_argument("--start", default=None, help="Optional ISO start datetime")
    parser.add_argument("--end", default=None, help="Optional ISO end datetime")
    parser.add_argument("--out", default="ml-pipeline/data/processed/training_dataset.csv", help="Dataset export path")
    parser.add_argument("--lookback", type=int, default=24, help="Lookback window for sequence preview")
    args = parser.parse_args()

    start = parse_dt(args.start)
    end = parse_dt(args.end)

    service = DatasetService(AQITimeSeriesRepository(get_influx_provider()))
    if args.station_id:
        dataset = service.build_station_dataset(station_id=args.station_id, start_at=start, end_at=end)
    else:
        dataset = service.build_city_dataset(city=args.city or "Delhi", start_at=start, end_at=end)

    export_path = service.export_training_dataset(dataset, args.out)
    split = service.split_train_validation_test(dataset)
    sequences, targets = service.prepare_sequence_windows(split["train"], lookback=args.lookback)
    summary = {
        **service.dataset_summary(dataset, export_path=export_path),
        "train_rows": len(split["train"]),
        "validation_rows": len(split["validation"]),
        "test_rows": len(split["test"]),
        "sequence_samples": len(sequences),
        "target_samples": len(targets),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
