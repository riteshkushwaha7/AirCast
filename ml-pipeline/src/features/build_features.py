from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class FeatureConfig:
    sequence_length: int = 48


def build_features(df: pd.DataFrame, sequence_length: int = 48) -> tuple[np.ndarray, np.ndarray]:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["hour"] = df["timestamp"].dt.hour
    df["dow"] = df["timestamp"].dt.dayofweek

    feature_cols = ["aqi", "aqi_rolling_3", "aqi_rolling_12", "hour", "dow"]
    values = df[feature_cols].to_numpy(dtype=np.float32)

    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for idx in range(sequence_length, len(values) - 24):
        xs.append(values[idx - sequence_length : idx])
        # Targets for 4h, 6h, 12h, 24h horizons based on AQI column
        ys.append(np.array([values[idx + 4][0], values[idx + 6][0], values[idx + 12][0], values[idx + 24][0]], dtype=np.float32))

    if not xs:
        return np.empty((0, sequence_length, len(feature_cols))), np.empty((0, 4))

    return np.stack(xs), np.stack(ys)
