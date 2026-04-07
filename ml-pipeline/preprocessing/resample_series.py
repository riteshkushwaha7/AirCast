import argparse
from pathlib import Path

import pandas as pd


def resample_dataframe(
    df: pd.DataFrame,
    frequency: str = "1h",
    short_gap_limit: int = 2,
    strategy: str = "ffill_then_interp",
) -> pd.DataFrame:
    frame = df.copy()
    frame["observed_at"] = pd.to_datetime(frame["observed_at"], utc=True).dt.floor("h")
    frame = frame.sort_values("observed_at").drop_duplicates(subset=["observed_at"], keep="last")
    frame["aqi"] = pd.to_numeric(frame["aqi"], errors="coerce")
    frame = frame.set_index("observed_at")

    out = frame[["aqi"]].resample(frequency).mean()
    missing_mask = out["aqi"].isna()
    filled = out["aqi"].copy()

    if strategy in {"ffill_then_interp", "forward_fill_only"}:
        filled = filled.ffill(limit=short_gap_limit)
    if strategy in {"ffill_then_interp", "interpolate_only"}:
        filled = filled.interpolate(method="time", limit=short_gap_limit, limit_direction="both")

    out["aqi"] = filled
    out["missing_flag"] = missing_mask.astype(int)
    out["imputed_flag"] = (missing_mask & out["aqi"].notna()).astype(int)
    return out.reset_index()


def main() -> None:
    parser = argparse.ArgumentParser(description="Resample AQI series to hourly points with missing/imputed flags")
    parser.add_argument("--input", required=True, help="Input CSV with observed_at and aqi columns")
    parser.add_argument("--output", default="data/processed/aqi_resampled.csv")
    parser.add_argument("--frequency", default="1H")
    parser.add_argument("--short-gap-limit", type=int, default=2)
    parser.add_argument("--strategy", default="ffill_then_interp")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    out = resample_dataframe(
        df=df,
        frequency=args.frequency,
        short_gap_limit=args.short_gap_limit,
        strategy=args.strategy,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    print(f"Resampled {len(out)} rows -> {output_path}")


if __name__ == "__main__":
    main()
