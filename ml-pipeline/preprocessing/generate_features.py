import argparse
from pathlib import Path

import pandas as pd


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["observed_at"] = pd.to_datetime(out["observed_at"], utc=True)
    out = out.sort_values("observed_at")
    out["hour_of_day"] = out["observed_at"].dt.hour
    out["day_of_week"] = out["observed_at"].dt.dayofweek
    out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
    out["rolling_avg_3h"] = out["aqi"].rolling(3, min_periods=1).mean()
    out["rolling_avg_6h"] = out["aqi"].rolling(6, min_periods=1).mean()
    out["rolling_avg_12h"] = out["aqi"].rolling(12, min_periods=1).mean()
    out["lag_1"] = out["aqi"].shift(1)
    out["lag_3"] = out["aqi"].shift(3)
    out["lag_6"] = out["aqi"].shift(6)
    out["lag_12"] = out["aqi"].shift(12)
    out["lag_24"] = out["aqi"].shift(24)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate forecasting features from resampled AQI data")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", default="data/processed/aqi_features.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    features = generate_features(df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    print(f"Feature rows: {len(features)} -> {output_path}")


if __name__ == "__main__":
    main()
