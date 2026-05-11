import json
import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.repositories.aqi_timeseries_repository import AQIPredictionRecord, AQITimeSeriesRepository
from app.utils.validators import aqi_to_category

logger = logging.getLogger(__name__)

_FORECAST_HORIZONS = [4, 6, 12, 24]

# Directory where per-city models are stored (relative to backend/)
_MODELS_DIR = Path(__file__).resolve().parents[2] / "models"


def _city_key(name: str) -> str:
    """Normalize a city name to match saved model filenames."""
    return "_".join(name.lower().strip().split())


class ModelNotTrainedError(RuntimeError):
    """Raised when the LSTM model file has not been saved yet."""


class PredictionService:
    """Loads per-city LSTM models and runs inference.  Falls back to
    trend-based heuristic when no model exists for the requested city."""

    _model_cache: dict[str, Any] = {}
    _meta_cache: dict[str, dict[str, Any]] = {}

    def __init__(self, timeseries_repository: AQITimeSeriesRepository) -> None:
        self.timeseries_repository = timeseries_repository
        self.settings = get_settings()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, city: str, location_id: str) -> dict[str, Any]:
        """Fetch history, run inference (LSTM or trend fallback), store results, return dict."""
        lookback = self.settings.lookback_hours
        history = self._fetch_history(city, lookback)

        aqi_series = [float(row["aqi"]) for row in history] if history else []

        city_key = _city_key(city)
        model, meta = self._try_load_city_model(city_key)

        if model is not None and meta is not None:
            predicted_values = self._run_lstm(model, meta, aqi_series, lookback)
            source = "model"
        elif aqi_series and len(aqi_series) >= 2:
            predicted_values = self._run_trend_fallback(aqi_series)
            source = "trend"
        else:
            predicted_values = self._run_trend_fallback([100.0, 100.0])
            source = "trend"

        now = datetime.now(tz=UTC)
        horizons_out: list[dict[str, Any]] = []

        for i, h in enumerate(_FORECAST_HORIZONS):
            pred_aqi = predicted_values[i] if i < len(predicted_values) else predicted_values[-1]
            pred_aqi = max(0.0, min(500.0, pred_aqi))
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

        self._persist(city=city, now=now, horizons=horizons_out, source=source)

        return {
            "location_id": location_id,
            "city": city,
            "generated_at": now.isoformat(),
            "horizons": horizons_out,
        }

    # ------------------------------------------------------------------
    # LSTM inference
    # ------------------------------------------------------------------

    def _run_lstm(self, model: Any, meta: dict[str, Any], aqi_series: list[float], lookback: int) -> list[float]:
        try:
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("numpy is required for prediction inference") from exc

        # Use normalization params from training metadata
        s_min = meta.get("series_min", 0.0)
        s_max = meta.get("series_max", 500.0)
        scale = s_max - s_min if s_max - s_min > 1e-6 else 1.0

        if not aqi_series:
            # No live data — use midpoint of training range
            midpoint = (s_min + s_max) / 2.0
            aqi_series = [midpoint] * lookback

        if len(aqi_series) < lookback:
            pad = [float(aqi_series[0])] * (lookback - len(aqi_series))
            aqi_series = pad + aqi_series
        else:
            aqi_series = aqi_series[-lookback:]

        arr = np.array(aqi_series, dtype=np.float32)
        arr_norm = (arr - s_min) / scale

        X = arr_norm.reshape(1, lookback, 1)
        raw_preds = np.array(model.predict(X, verbose=0)).flatten()
        denorm = raw_preds * scale + s_min
        return [float(v) for v in np.clip(denorm, 0.0, 500.0)]

    # ------------------------------------------------------------------
    # Trend-based fallback (no model needed)
    # ------------------------------------------------------------------

    @staticmethod
    def _run_trend_fallback(aqi_series: list[float]) -> list[float]:
        """Simple moving-average + drift heuristic when no LSTM model is available."""
        recent = aqi_series[-min(6, len(aqi_series)):]
        avg = sum(recent) / len(recent)
        drift_per_hour = (recent[-1] - recent[0]) / max(len(recent), 1) * 0.5

        predictions: list[float] = []
        for h in _FORECAST_HORIZONS:
            pred = avg + drift_per_hour * h
            pred += (h / 24.0) * 5.0
            predictions.append(max(0.0, min(500.0, round(pred, 1))))
        return predictions

    # ------------------------------------------------------------------
    # Per-city model loading
    # ------------------------------------------------------------------

    def _try_load_city_model(self, city_key: str) -> tuple[Any | None, dict[str, Any] | None]:
        """Try to load a per-city LSTM model from models/<city_key>.keras."""
        if city_key in PredictionService._model_cache:
            return PredictionService._model_cache[city_key], PredictionService._meta_cache.get(city_key)

        model_path = _MODELS_DIR / f"{city_key}.keras"
        meta_path = _MODELS_DIR / f"{city_key}.meta.json"

        if not model_path.exists():
            logger.info("[Prediction] No model for city=%s at %s — using fallback", city_key, model_path)
            return None, None

        try:
            try:
                import tensorflow as tf  # type: ignore[import]
                loaded = tf.keras.models.load_model(str(model_path))
            except ImportError:
                import keras  # type: ignore[import]
                loaded = keras.models.load_model(str(model_path))

            PredictionService._model_cache[city_key] = loaded
            logger.info("[Prediction] Loaded model for city=%s from %s", city_key, model_path)
        except Exception as exc:
            logger.warning("[Prediction] Failed to load model for city=%s: %s", city_key, exc)
            return None, None

        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                PredictionService._meta_cache[city_key] = meta
            except Exception:
                pass

        return loaded, meta

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_history(self, city: str, lookback_hours: int) -> list[dict[str, Any]]:
        end_at = datetime.now(tz=UTC)
        start_at = end_at - timedelta(hours=lookback_hours)
        try:
            rows = self.timeseries_repository.read_raw_records(
                start_at=start_at, end_at=end_at, city=city
            )
            return [row for row in rows if row.get("aqi") is not None]
        except Exception as exc:
            logger.warning("[Prediction] Failed to fetch history for city=%s: %s", city, exc)
            return []

    def _persist(self, city: str, now: datetime, horizons: list[dict[str, Any]], source: str = "model") -> None:
        records = [
            AQIPredictionRecord(
                model_name="lstm" if source == "model" else "trend",
                city=city,
                forecast_horizon=h["horizon_hours"],
                source=source,
                predicted_aqi=h["predicted_aqi"],
                confidence_score=None,
                predicted_category=h["category"],
                target_timestamp=now + timedelta(hours=h["horizon_hours"]),
                generated_timestamp=now,
                timestamp=now,
            )
            for h in horizons
        ]
        try:
            written = self.timeseries_repository.write_prediction_records(records)
            logger.info("[Prediction] Stored %d %s prediction records for city=%s", written, source, city)
        except Exception as exc:
            logger.warning("[Prediction] Failed to persist predictions for city=%s: %s", city, exc)
