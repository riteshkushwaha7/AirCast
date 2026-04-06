"""Fetch near-real-time AQI data from CPCB/OGD-like endpoints into raw storage.

This script is intentionally connector-agnostic in the prototype.
"""

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="New Delhi")
    parser.add_argument("--out", default="data/raw/aqi_cpcb_latest.csv")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sample = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-04-01", periods=24, freq="H"),
            "city": [args.city] * 24,
            "aqi": [142, 138, 136, 141, 149, 158, 166, 172, 176, 180, 184, 188, 186, 179, 171, 166, 160, 154, 148, 143, 140, 138, 136, 134],
        }
    )
    sample.to_csv(out_path, index=False)
    print(f"Wrote {len(sample)} rows to {out_path}")


if __name__ == "__main__":
    main()
