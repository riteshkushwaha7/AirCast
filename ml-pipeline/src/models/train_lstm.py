import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
import yaml
from sklearn.model_selection import train_test_split

from src.features.build_features import build_features
from src.models.registry import register_model


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def build_model(sequence_length: int, feature_count: int, learning_rate: float) -> tf.keras.Model:
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(sequence_length, feature_count)),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.Dropout(0.15),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(4),
        ]
    )
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss="mse", metrics=["mae"])
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--data", default="data/processed/aqi_processed.csv")
    args = parser.parse_args()

    config = load_config(args.config)
    sequence_length = int(config["model"]["sequence_length"])

    df = pd.read_csv(args.data)
    x, y = build_features(df, sequence_length=sequence_length)
    if len(x) < 20:
        raise RuntimeError("Not enough samples after feature generation. Add more historical data.")

    x_train, x_temp, y_train, y_temp = train_test_split(x, y, test_size=0.3, random_state=42)
    x_val, x_test, y_val, y_test = train_test_split(x_temp, y_temp, test_size=0.5, random_state=42)

    model = build_model(
        sequence_length=sequence_length,
        feature_count=x.shape[2],
        learning_rate=float(config["training"]["learning_rate"]),
    )

    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=int(config["training"]["epochs"]),
        batch_size=int(config["training"]["batch_size"]),
        verbose=1,
    )

    loss, mae = model.evaluate(x_test, y_test, verbose=0)

    registry = Path(config["paths"]["registry"])
    metadata = {
        "model_name": config["model"]["name"],
        "version": config["model"]["version"],
        "metrics": {"test_loss": float(loss), "test_mae": float(mae)},
        "feature_count": int(x.shape[2]),
        "sequence_length": sequence_length,
    }
    model_dir = register_model(registry, metadata)
    model.save(model_dir / "model.keras")

    (model_dir / "history.json").write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    print(json.dumps({"model_dir": str(model_dir), "metrics": metadata["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
