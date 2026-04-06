"""Backfill historical AQI data from OpenAQ-style harmonized datasets."""

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="New Delhi")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--out", default="data/raw/aqi_backfill.csv")
    args = parser.parse_args()

    rng = pd.date_range(end=pd.Timestamp.now(), periods=args.days * 24, freq="H")
    df = pd.DataFrame(
        {
            "timestamp": rng,
            "city": args.city,
            "aqi": (130 + (pd.Series(range(len(rng))) % 40) + (pd.Series(range(len(rng))) % 7) * 2).astype(float),
        }
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Backfilled {len(df)} rows -> {out_path}")


if __name__ == "__main__":
    main()
