import argparse
import json
from pathlib import Path

from ingestion.kaggle_loader import KaggleHistoricalLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Kaggle AQI dataset columns and AirWise column mapping")
    parser.add_argument("--dataset-path", required=True, help="Path to Kaggle CSV file or extracted folder")
    parser.add_argument("--city", default="Delhi", help="City filter to validate early (default: Delhi)")
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    args = parser.parse_args()

    loader = KaggleHistoricalLoader(dataset_path=args.dataset_path, default_city=args.city)
    resolved_csv = loader.resolve_csv_path()
    columns = loader.inspect_columns()
    mapped_columns = loader.column_map()
    sample_count = len(loader.load_raw_dataframe(city=args.city).head(200))

    result = {
        "dataset_path": str(resolved_csv),
        "city_preview": args.city,
        "preview_row_count": sample_count,
        "columns": columns,
        "airwise_column_mapping": mapped_columns,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
