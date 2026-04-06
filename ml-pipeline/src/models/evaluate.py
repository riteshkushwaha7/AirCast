import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", default="data/processed/aqi_processed.csv")
    args = parser.parse_args()

    model_path = Path(args.model)
    if model_path.is_dir() and (model_path / "model.keras").exists():
        model_path = model_path / "model.keras"

    model = tf.keras.models.load_model(model_path)

    df = pd.read_csv(args.data)
    sample = df[["aqi", "aqi_rolling_3", "aqi_rolling_12"]].tail(48).to_numpy(dtype=np.float32)
    hours = np.arange(48, dtype=np.float32).reshape(-1, 1) % 24
    dows = np.arange(48, dtype=np.float32).reshape(-1, 1) % 7
    x = np.concatenate([sample, hours, dows], axis=1)[None, ...]

    pred = model.predict(x, verbose=0)[0]
    output = {
        "forecast_4h": round(float(pred[0]), 1),
        "forecast_6h": round(float(pred[1]), 1),
        "forecast_12h": round(float(pred[2]), 1),
        "forecast_24h": round(float(pred[3]), 1),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
