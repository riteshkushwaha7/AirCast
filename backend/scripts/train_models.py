"""Train unified AirWise LSTM model on cleaned AQI data."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import (Concatenate, Dense, Dropout, Embedding,
                                     Flatten, Input, LSTM)
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
DATA_PATH = BACKEND_DIR / "data" / "aqi_clean.csv"
ALT_DATA_PATH = BACKEND_DIR / "data" / "aqi.csv"
MODELS_DIR = BACKEND_DIR / "models"
ENV_PATH = BACKEND_DIR / ".env"

TARGET_CITIES = [
    "Delhi", "Noida", "Gurugram", "Faridabad", "Ghaziabad",
    "Mumbai", "Pune", "Nagpur", "Bengaluru", "Chennai",
    "Hyderabad", "Kolkata", "Ahmedabad", "Surat", "Jaipur",
    "Jodhpur", "Lucknow", "Kanpur", "Varanasi", "Agra",
    "Patna", "Bhopal", "Indore", "Chandigarh", "Ludhiana",
    "Amritsar", "Visakhapatnam", "Vijayawada", "Kochi",
    "Thiruvananthapuram", "Coimbatore", "Madurai", "Dehradun",
    "Ranchi", "Bhubaneswar", "Guwahati",
]

LOOKBACK_DEFAULT = 30
HORIZONS_DEFAULT = [1, 2, 3, 7]
MIN_DAYS_PER_CITY = 90
MIN_SEQUENCES_PER_CITY = 10
SPLIT_RATIOS = (0.7, 0.15, 0.15)
SCALER_PATH = MODELS_DIR / "airwise_scaler.pkl"
MODEL_PATH = MODELS_DIR / "airwise_lstm.keras"
METADATA_PATH = MODELS_DIR / "airwise_metadata.json"


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def load_env() -> None:
    if load_dotenv and ENV_PATH.exists():
        load_dotenv(ENV_PATH)


def get_training_hyperparams() -> Tuple[int, List[int]]:
    lookback = int(os.getenv("LOOKBACK_HOURS", LOOKBACK_DEFAULT))
    horizons_raw = os.getenv("FORECAST_HORIZONS")
    if horizons_raw:
        horizons = [int(h.strip()) for h in horizons_raw.split(",") if h.strip()]
    else:
        horizons = HORIZONS_DEFAULT
    return lookback, horizons


def clean_models_dir() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.keras", "*.h5", "*.pkl", "*.json"):
        for path in MODELS_DIR.glob(pattern):
            path.unlink(missing_ok=True)


def forward_fill_then_interpolate(series: pd.Series, limit: int) -> pd.Series:
    series = series.ffill(limit=limit)
    return series.interpolate(limit=limit, limit_direction="forward")


def _resolve_data_path() -> Path:
    if DATA_PATH.exists():
        return DATA_PATH
    if ALT_DATA_PATH.exists():
        print(f"[INFO] Using fallback dataset: {ALT_DATA_PATH.name}")
        return ALT_DATA_PATH
    raise FileNotFoundError(
        f"Data file not found: {DATA_PATH} (fallback {ALT_DATA_PATH} not found either)"
    )


def load_and_validate_data() -> Tuple[pd.DataFrame, List[str], List[str]]:
    data_file = _resolve_data_path()
    df = pd.read_csv(data_file)

    rename_map = {
        "area": "city",
        "aqi_value": "aqi",
        "prominent_pollutants": "prominent_pollutant",
        "air_quality_status": "status",
    }
    df = df.rename(columns=rename_map)

    required_cols = {"date", "city", "aqi"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(
            "CSV must contain columns: date, city, aqi (missing: " + ", ".join(sorted(missing)) + ")"
        )

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df["city"] = df["city"].astype(str).str.strip()
    df = df.dropna(subset=["date", "aqi"])
    df = df[df["aqi"] > 0]
    df = df[df["city"].isin(TARGET_CITIES)]

    cities_found = sorted(df["city"].unique())
    cities_missing = [city for city in TARGET_CITIES if city not in cities_found]

    processed_frames: List[pd.DataFrame] = []
    cities_ready: List[str] = []
    cities_skipped: List[str] = []

    for city in TARGET_CITIES:
        city_df = df[df["city"] == city].copy()
        if city_df.empty:
            cities_skipped.append(city)
            continue

        city_df = (
            city_df.set_index("date")["aqi"].resample("1D").mean().to_frame(name="aqi")
        )
        city_df["aqi"] = forward_fill_then_interpolate(city_df["aqi"], limit=7)
        city_df = city_df.dropna(subset=["aqi"]).reset_index().sort_values("date")
        city_df["city"] = city

        if len(city_df) < MIN_DAYS_PER_CITY:
            print(f"[WARN] Skipping {city}: only {len(city_df)} days (<{MIN_DAYS_PER_CITY}).")
            cities_skipped.append(city)
            continue

        processed_frames.append(city_df)
        cities_ready.append(city)

    if not processed_frames:
        raise RuntimeError("No cities with ≥90 days of data.")

    combined = pd.concat(processed_frames, ignore_index=True)
    print(f"Cities found: {', '.join(cities_found) if cities_found else 'None'}")
    if cities_missing:
        print(f"Cities missing from data: {', '.join(cities_missing)}")

    return combined, cities_ready, cities_skipped


def build_sequences(
    df: pd.DataFrame,
    lookback: int,
    horizons: List[int],
    city_encoder: Dict[str, int],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]:
    X_train_aqi_list: List[np.ndarray] = []
    X_val_aqi_list: List[np.ndarray] = []
    X_test_aqi_list: List[np.ndarray] = []
    X_train_city_list: List[np.ndarray] = []
    X_val_city_list: List[np.ndarray] = []
    X_test_city_list: List[np.ndarray] = []
    y_train_list: List[np.ndarray] = []
    y_val_list: List[np.ndarray] = []
    y_test_list: List[np.ndarray] = []

    cities_used: List[str] = []
    cities_sequence_skipped: List[str] = []

    for city in TARGET_CITIES:
        city_df = df[df["city"] == city].copy()
        if city_df.empty:
            continue

        values = city_df["aqi_scaled"].to_numpy(dtype=np.float32)
        city_id = city_encoder[city]

        sequences: List[np.ndarray] = []
        labels: List[np.ndarray] = []

        for idx in range(lookback, len(values)):
            window = values[idx - lookback : idx]
            targets: List[float] = []
            valid = True
            for horizon in horizons:
                target_idx = idx + horizon
                if target_idx >= len(values):
                    valid = False
                    break
                targets.append(values[target_idx])
            if not valid:
                continue
            sequences.append(window)
            labels.append(np.array(targets, dtype=np.float32))

        if len(sequences) < MIN_SEQUENCES_PER_CITY:
            print(f"[WARN] Skipping {city}: only {len(sequences)} usable sequences (need ≥{MIN_SEQUENCES_PER_CITY}).")
            cities_sequence_skipped.append(city)
            continue

        seqs = np.stack(sequences)
        labs = np.stack(labels)
        city_ids = np.full((len(seqs), 1), city_id, dtype=np.int32)

        n = len(seqs)
        train_count = max(int(n * SPLIT_RATIOS[0]), 1)
        val_count = max(int(n * SPLIT_RATIOS[1]), 1)
        test_count = n - train_count - val_count

        if test_count <= 0:
            if val_count > 1:
                val_count -= 1
                test_count = 1
            elif train_count > 1:
                train_count -= 1
                test_count = 1
            else:
                print(f"[WARN] Skipping {city}: unable to split sequences.")
                cities_sequence_skipped.append(city)
                continue

        train_end = train_count
        val_end = train_end + val_count

        if val_end >= n:
            val_end = n - test_count
        if val_end <= train_end or n - val_end < test_count:
            print(f"[WARN] Skipping {city}: invalid split sizes.")
            cities_sequence_skipped.append(city)
            continue

        X_train_aqi_list.append(seqs[:train_end])
        X_val_aqi_list.append(seqs[train_end:val_end])
        X_test_aqi_list.append(seqs[val_end:])

        X_train_city_list.append(city_ids[:train_end])
        X_val_city_list.append(city_ids[train_end:val_end])
        X_test_city_list.append(city_ids[val_end:])

        y_train_list.append(labs[:train_end])
        y_val_list.append(labs[train_end:val_end])
        y_test_list.append(labs[val_end:])

        cities_used.append(city)

    def concat_or_empty(chunks: List[np.ndarray], shape: Tuple[int, ...], dtype) -> np.ndarray:
        if chunks:
            return np.concatenate(chunks, axis=0)
        return np.empty(shape, dtype=dtype)

    horizons_len = len(horizons)
    X_train_aqi = concat_or_empty(X_train_aqi_list, (0, lookback), np.float32)
    X_val_aqi = concat_or_empty(X_val_aqi_list, (0, lookback), np.float32)
    X_test_aqi = concat_or_empty(X_test_aqi_list, (0, lookback), np.float32)

    X_train_city = concat_or_empty(X_train_city_list, (0, 1), np.int32)
    X_val_city = concat_or_empty(X_val_city_list, (0, 1), np.int32)
    X_test_city = concat_or_empty(X_test_city_list, (0, 1), np.int32)

    y_train = concat_or_empty(y_train_list, (0, horizons_len), np.float32)
    y_val = concat_or_empty(y_val_list, (0, horizons_len), np.float32)
    y_test = concat_or_empty(y_test_list, (0, horizons_len), np.float32)

    return (
        X_train_aqi,
        X_val_aqi,
        X_test_aqi,
        X_train_city,
        X_val_city,
        X_test_city,
        y_train,
        y_val,
        y_test,
        cities_used,
        cities_sequence_skipped,
    )


def build_model(num_cities: int, lookback: int, horizons: List[int]) -> Model:
    input_aqi = Input(shape=(lookback, 1), name="aqi_sequence")
    input_city = Input(shape=(1,), name="city_id")

    x = LSTM(128, return_sequences=True)(input_aqi)
    x = Dropout(0.2)(x)
    x = LSTM(64, return_sequences=False)(x)
    x = Dropout(0.2)(x)
    x = Dense(64, activation="relu")(x)

    city_embed = Embedding(input_dim=num_cities, output_dim=8, name="city_embedding")(input_city)
    city_embed = Flatten()(city_embed)

    combined = Concatenate()([x, city_embed])
    combined = Dense(64, activation="relu")(combined)
    combined = Dense(32, activation="relu")(combined)

    output = Dense(len(horizons), activation="linear", name="forecasts")(combined)

    model = Model(inputs=[input_aqi, input_city], outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001), loss="mse", metrics=["mae"])
    model.summary()
    return model


def inverse_scale(values: np.ndarray, scaler: MinMaxScaler) -> np.ndarray:
    reshaped = values.reshape(-1, 1)
    inv = scaler.inverse_transform(reshaped)
    return inv.reshape(values.shape)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    horizons: List[int],
) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
    mae_scores: Dict[str, float] = {}
    rmse_scores: Dict[str, float] = {}
    mape_scores: Dict[str, float] = {}
    epsilon = 1e-6

    for idx, horizon in enumerate(horizons):
        true_vals = y_true[:, idx]
        pred_vals = y_pred[:, idx]
        mae_scores[f"day{horizon}"] = float(mean_absolute_error(true_vals, pred_vals))
        mse = mean_squared_error(true_vals, pred_vals)
        rmse_scores[f"day{horizon}"] = float(np.sqrt(mse))
        mape_scores[f"day{horizon}"] = float(
            np.mean(np.abs((true_vals - pred_vals) / np.maximum(true_vals, epsilon))) * 100
        )

    return mae_scores, rmse_scores, mape_scores


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def main() -> None:
    load_env()
    lookback, horizons = get_training_hyperparams()
    print(f"Using lookback={lookback} days, horizons={horizons}")

    data, cities_ready, cities_skipped_initial = load_and_validate_data()
    city_encoder = {city: idx for idx, city in enumerate(TARGET_CITIES)}

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(data[["aqi"]])
    data["aqi_scaled"] = scaler.transform(data[["aqi"]])

    (
        X_train_aqi,
        X_val_aqi,
        X_test_aqi,
        X_train_city,
        X_val_city,
        X_test_city,
        y_train,
        y_val,
        y_test,
        cities_used,
        cities_sequence_skipped,
    ) = build_sequences(data, lookback, horizons, city_encoder)

    if min(len(X_train_aqi), len(X_val_aqi), len(X_test_aqi)) == 0:
        raise RuntimeError("Insufficient samples after sequence building. Cannot train model.")

    X_train_aqi = X_train_aqi.reshape(-1, lookback, 1)
    X_val_aqi = X_val_aqi.reshape(-1, lookback, 1)
    X_test_aqi = X_test_aqi.reshape(-1, lookback, 1)
    X_train_city = X_train_city.reshape(-1, 1)
    X_val_city = X_val_city.reshape(-1, 1)
    X_test_city = X_test_city.reshape(-1, 1)

    clean_models_dir()

    model = build_model(len(TARGET_CITIES), lookback, horizons)
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True, verbose=1),
        ModelCheckpoint(filepath=str(MODEL_PATH), monitor="val_loss", save_best_only=True, verbose=1),
    ]

    history = model.fit(
        [X_train_aqi, X_train_city],
        y_train,
        validation_data=([X_val_aqi, X_val_city], y_val),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1,
    )

    best_val_loss = float(np.min(history.history.get("val_loss", [np.nan])))

    # Load the best model saved by ModelCheckpoint for evaluation
    best_model = load_model(MODEL_PATH)
    preds_scaled = best_model.predict([X_test_aqi, X_test_city], verbose=0)
    preds = inverse_scale(preds_scaled, scaler)
    y_true = inverse_scale(y_test, scaler)

    mae_scores, rmse_scores, mape_scores = compute_metrics(y_true, preds, horizons)

    dump(scaler, SCALER_PATH)

    metadata = {
        "cities": TARGET_CITIES,
        "city_encoder": city_encoder,
        "lookback_days": lookback,
        "horizons_days": horizons,
        "total_samples": int(len(X_train_aqi) + len(X_val_aqi) + len(X_test_aqi)),
        "train_samples": int(len(X_train_aqi)),
        "val_samples": int(len(X_val_aqi)),
        "test_samples": int(len(X_test_aqi)),
        "mae_per_horizon": mae_scores,
        "rmse_per_horizon": rmse_scores,
        "mape_per_horizon": mape_scores,
        "cities_trained": sorted(cities_used),
        "cities_skipped": sorted(set(cities_skipped_initial + cities_sequence_skipped)),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "scaler_feature_range": [0, 1],
    }

    with METADATA_PATH.open("w", encoding="utf-8") as fp:
        json.dump(metadata, fp, indent=2)

    print("-" * 50)
    print(f"Cities successfully trained: {len(cities_used)} / {len(TARGET_CITIES)}")
    skipped_display = metadata["cities_skipped"] or ["None"]
    print(f"Cities skipped (<{MIN_DAYS_PER_CITY} days or insufficient sequences): {', '.join(skipped_display)}")
    print(f"Total samples used: {metadata['total_samples']}")
    print(f"Best val_loss: {best_val_loss:.5f}")
    print("MAE / RMSE / MAPE per horizon:")
    for horizon in horizons:
        key = f"day{horizon}"
        print(
            f"  {key}: MAE={mae_scores[key]:.3f} | "
            f"RMSE={rmse_scores[key]:.3f} | MAPE={mape_scores[key]:.2f}%"
        )
    print(f"Artifacts saved to {MODELS_DIR}")


if __name__ == "__main__":
    main()
