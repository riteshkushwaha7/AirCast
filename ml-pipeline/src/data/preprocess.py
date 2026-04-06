import argparse
from pathlib import Path

import pandas as pd


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"])
    df["aqi"] = df["aqi"].clip(lower=0, upper=500)
    df["aqi_rolling_3"] = df["aqi"].rolling(3, min_periods=1).mean()
    df["aqi_rolling_12"] = df["aqi"].rolling(12, min_periods=1).mean()
    df = df.dropna()
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/processed/aqi_processed.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    processed = preprocess(df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_path, index=False)
    print(f"Processed {len(processed)} rows -> {output_path}")


if __name__ == "__main__":
    main()
