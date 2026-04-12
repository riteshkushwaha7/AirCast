import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

from forecasting.planner_projection import DailyPlannerProjection, project_weekly_daily_aqi


def load_recent_series(input_path: str | None) -> pd.Series:
    if input_path is None:
        return pd.Series(dtype="float64")
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    frame = pd.read_csv(path)
    if "aqi" not in frame.columns:
        raise ValueError("Input file must include an 'aqi' column")
    return pd.to_numeric(frame["aqi"], errors="coerce").dropna()


def run_weekly_projection(input_path: str | None, days: int = 7) -> list[DailyPlannerProjection]:
    series = load_recent_series(input_path)
    return project_weekly_daily_aqi(
        recent_series=series,
        start_date=date.today(),
        days=days,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate weekly AQI planner projection from recent AQI series")
    parser.add_argument("--input", default=None, help="Optional CSV with 'aqi' column from processed data")
    parser.add_argument("--days", type=int, default=7, help="Projection horizon in days")
    parser.add_argument("--output", default="data/processed/weekly_planner_projection.json")
    args = parser.parse_args()

    projections = run_weekly_projection(args.input, days=args.days)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([item.__dict__ for item in projections], indent=2),
        encoding="utf-8",
    )
    print(f"Generated {len(projections)} planner projections -> {output_path}")


if __name__ == "__main__":
    main()
