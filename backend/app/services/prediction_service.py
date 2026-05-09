import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings
from app.repositories.aqi_timeseries_repository import AQIPredictionRecord, AQITimeSeriesRepository
from app.utils.validators import aqi_to_category

logger = logging.getLogger(__name__)

_FORECAST_HORIZONS = [4, 6, 12, 24]


class ModelNotTrainedError(RuntimeError):
    """Raised when the LSTM model file has not been saved yet."""


class PredictionService:
    """Runs LSTM inference for a city and persists results in InfluxDB."""

    _cached_model: Any = None
    _cached_model_path: str | None = None

    def __init__(self, timeseries_repository: AQITimeSeriesRepository) -> None:
        self.timeseries_repository = timeseries_repository
        self.settings = get_settings()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, city: str, location_id: str) -> dict[str, Any]:
        """Fetch history, run LSTM inference, store results, return dict.

        Raises:
            ModelNotTrainedError: if the model file does not exist.
            ValueError: if there is insufficient historical data.
        """
        model = self._load_model()

        try:
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("numpy is required for prediction inference") from exc

        lookback = self.settings.lookback_hours
        history = self._fetch_history(city, lookback)

        if len(history) < 4:
            raise ValueError(
                f"Not enough historical AQI data for {city} "
                f"(found {len(history)}, need at least 4 readings)."
            )

        aqi_series = [float(row["aqi"]) for row in history]

        if len(aqi_series) < lookback:
            pad = [float(aqi_series[0])] * (lookback - len(aqi_series))
            aqi_series = pad + aqi_series
        else:
            aqi_series = aqi_series[-lookback:]

        arr = np.array(aqi_series, dtype=np.float32)
        arr_min = float(arr.min())
        arr_max = float(arr.max())
        scale = arr_max - arr_min if arr_max - arr_min > 1e-6 else 1.0
        arr_norm = (arr - arr_min) / scale

        X = arr_norm.reshape(1, lookback, 1)

        raw_preds = np.array(model.predict(X, verbose=0)).flatten()  # type: ignore[union-attr]

        raw_preds_denorm = np.clip(raw_preds * scale + arr_min, 0.0, 500.0)

        now = datetime.now(tz=UTC)
        horizons_out: list[dict[str, Any]] = []

        for i, h in enumerate(_FORECAST_HORIZONS):
            pred_aqi = float(raw_preds_denorm[i]) if i < len(raw_preds_denorm) else float(raw_preds_denorm[-1])
            category = aqi_to_category(pred_aqi).value
            target_ts = now + timedelta(hours=h)
            horizons_out.append(
                {
                    "horizon_hours": h,
                    "predicted_aqi": round(pred_aqi, 1),
                    "category": category,
                    "target_timestamp": target_ts.isoformat(),
                }
            )

        self._persist(city=city, now=now, horizons=horizons_out)

        return {
            "location_id": location_id,
            "city": city,
            "generated_at": now.isoformat(),
            "horizons": horizons_out,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_model(self) -> Any:
        model_path = self.settings.lstm_model_path
        if PredictionService._cached_model is not None and PredictionService._cached_model_path == model_path:
            return PredictionService._cached_model

        if not model_path or not os.path.exists(model_path):
            raise ModelNotTrainedError(
                "Model not trained yet. Please train the model first."
            )

        try:
            try:
                import tensorflow as tf  # type: ignore[import]
                loaded = tf.keras.models.load_model(model_path)
            except ImportError:
                import keras  # type: ignore[import]
                loaded = keras.models.load_model(model_path)

            PredictionService._cached_model = loaded
            PredictionService._cached_model_path = model_path
            logger.info("[Prediction] LSTM model loaded from %s", model_path)
            return loaded
        except Exception as exc:
            raise RuntimeError(f"Failed to load LSTM model from {model_path}: {exc}") from exc

    def _fetch_history(self, city: str, lookback_hours: int) -> list[dict[str, Any]]:
        end_at = datetime.now(tz=UTC)
        start_at = end_at - timedelta(hours=lookback_hours)
        rows = self.timeseries_repository.read_raw_records(
            start_at=start_at, end_at=end_at, city=city
        )
        return [row for row in rows if row.get("aqi") is not None]

    def _persist(self, city: str, now: datetime, horizons: list[dict[str, Any]]) -> None:
        records = [
            AQIPredictionRecord(
                model_name="lstm",
                city=city,
                forecast_horizon=h["horizon_hours"],
                source="model",
                predicted_aqi=h["predicted_aqi"],
                confidence_score=None,
                predicted_category=h["category"],
                target_timestamp=now + timedelta(hours=h["horizon_hours"]),
                generated_timestamp=now,
                timestamp=now,
            )
            for h in horizons
        ]
        written = self.timeseries_repository.write_prediction_records(records)
        logger.info("[Prediction] Stored %d LSTM prediction records for city=%s", written, city)
