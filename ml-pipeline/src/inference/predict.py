import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf


def aqi_to_category(aqi: float) -> str:
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for sensitive users"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very unhealthy"
    return "Hazardous"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--aqi-seq", required=True, help="Comma-separated AQI values for latest sequence")
    args = parser.parse_args()

    model_path = Path(args.model)
    if model_path.is_dir() and (model_path / "model.keras").exists():
        model_path = model_path / "model.keras"

    model = tf.keras.models.load_model(model_path)

    aqi_values = [float(v.strip()) for v in args.aqi_seq.split(",") if v.strip()]
    if len(aqi_values) < 48:
        aqi_values = ([aqi_values[0]] * (48 - len(aqi_values))) + aqi_values

    arr = np.array(aqi_values[-48:], dtype=np.float32)
    rolling3 = np.convolve(arr, np.ones(3) / 3, mode="same")
    rolling12 = np.convolve(arr, np.ones(12) / 12, mode="same")
    hours = np.arange(48, dtype=np.float32)
    dows = (np.arange(48, dtype=np.float32) // 24) % 7

    x = np.stack([arr, rolling3, rolling12, hours, dows], axis=1)[None, ...]
    pred = model.predict(x, verbose=0)[0]

    horizons = [4, 6, 12, 24]
    forecasts = []
    for idx, horizon in enumerate(horizons):
        val = float(pred[idx])
        forecasts.append({"horizon_hours": horizon, "aqi": round(val, 1), "category": aqi_to_category(val)})

    daily_outlook = []
    base = float(np.mean(pred))
    for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        val = base + i * 3 - 4
        daily_outlook.append({"day": day, "avg_aqi": round(val, 1), "category": aqi_to_category(val)})

    print(json.dumps({"forecast": forecasts, "daily_outlook": daily_outlook}, indent=2))


if __name__ == "__main__":
    main()
