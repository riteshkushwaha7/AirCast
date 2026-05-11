import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.repositories.aqi_timeseries_repository import AQIPredictionRecord, AQITimeSeriesRepository
from app.utils.validators import aqi_to_category

logger = logging.getLogger(__name__)

_MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
_UNIFIED_MODEL_PATH = _MODELS_DIR / "airwise_lstm.keras"
_UNIFIED_SCALER_PATH = _MODELS_DIR / "airwise_scaler.pkl"
_UNIFIED_METADATA_PATH = _MODELS_DIR / "airwise_metadata.json"

# Forecast horizons in days; exposed as hours in the API response
_FORECAST_DAYS = [1, 2, 3, 7]
_FORECAST_HOURS = [d * 24 for d in _FORECAST_DAYS]  # [24, 48, 72, 168]

LOOKBACK_DAYS = 30


class ModelNotTrainedError(RuntimeError):
    """Raised when the LSTM model file has not been saved yet."""


class PredictionService:
    """Runs AQI predictions using the unified airwise LSTM model (dual inputs:
    aqi_sequence + city_id).  Falls back to a trend heuristic when the model
    file is absent."""

    _model: Any = None
    _scaler: Any = None
    _metadata: dict[str, Any] | None = None
    _model_loaded: bool = False

    def __init__(self, timeseries_repository: AQITimeSeriesRepository) -> None:
        self.timeseries_repository = timeseries_repository
        self.settings = get_settings()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, city: str, location_id: str) -> dict[str, Any]:
        """Fetch history, run inference (LSTM or trend fallback), store results, return dict."""
        history = self._fetch_history(city, lookback_hours=LOOKBACK_DAYS * 24)
        aqi_series = self._to_daily_series(history, LOOKBACK_DAYS)

        model, scaler, metadata = self._try_load_unified_model()
        city_encoder: dict[str, int] = (metadata or {}).get("city_encoder", {})

        if model is not None and scaler is not None and metadata is not None and city in city_encoder:
            predicted_values = self._run_lstm(model, scaler, city_encoder[city], aqi_series)
            source = "model"
        elif len(aqi_series) >= 2:
            predicted_values = self._run_trend_fallback(aqi_series)
            source = "trend"
        else:
            predicted_values = self._run_trend_fallback([100.0, 100.0])
            source = "trend"

        now = datetime.now(tz=UTC)
        horizons_out: list[dict[str, Any]] = []

        for i, (days, hours) in enumerate(zip(_FORECAST_DAYS, _FORECAST_HOURS)):
            pred_aqi = predicted_values[i] if i < len(predicted_values) else predicted_values[-1]
            pred_aqi = max(0.0, min(500.0, pred_aqi))
            category = aqi_to_category(pred_aqi).value
            target_ts = now + timedelta(hours=hours)
            horizons_out.append(
                {
                    "horizon_hours": hours,
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

    def _run_lstm(
        self,
        model: Any,
        scaler: Any,
        city_id: int,
        aqi_series: list[float],
    ) -> list[float]:
        try:
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("numpy is required for prediction inference") from exc

        series = list(aqi_series)
        if len(series) < LOOKBACK_DAYS:
            pad_val = series[0] if series else 100.0
            series = [pad_val] * (LOOKBACK_DAYS - len(series)) + series
        else:
            series = series[-LOOKBACK_DAYS:]

        arr = np.array(series, dtype=np.float32).reshape(-1, 1)
        arr_scaled = scaler.transform(arr)                         # (30, 1)

        X_aqi = arr_scaled.reshape(1, LOOKBACK_DAYS, 1)           # (1, 30, 1)
        X_city = np.array([[city_id]], dtype=np.int32)             # (1, 1)

        preds_scaled = model.predict([X_aqi, X_city], verbose=0)  # (1, 4)
        preds = scaler.inverse_transform(preds_scaled.T).flatten() # (4,)
        return [float(v) for v in np.clip(preds, 0.0, 500.0)]

    # ------------------------------------------------------------------
    # Trend-based fallback (no model needed)
    # ------------------------------------------------------------------

    @staticmethod
    def _run_trend_fallback(aqi_series: list[float]) -> list[float]:
        """Simple moving-average + drift heuristic when no LSTM model is available."""
        recent = aqi_series[-min(6, len(aqi_series)):]
        avg = sum(recent) / len(recent)
        drift_per_day = (recent[-1] - recent[0]) / max(len(recent), 1) * 0.5

        predictions: list[float] = []
        for days in _FORECAST_DAYS:
            pred = avg + drift_per_day * days + (days / 7.0) * 5.0
            predictions.append(max(0.0, min(500.0, round(pred, 1))))
        return predictions

    # ------------------------------------------------------------------
    # Unified model loading (cached)
    # ------------------------------------------------------------------

    def _try_load_unified_model(self) -> tuple[Any | None, Any | None, dict[str, Any] | None]:
        """Load (and cache at class level) airwise_lstm.keras, scaler, and metadata."""
        if PredictionService._model_loaded:
            return PredictionService._model, PredictionService._scaler, PredictionService._metadata

        PredictionService._model_loaded = True  # mark attempted so we don't retry every request

        if not _UNIFIED_MODEL_PATH.exists():
            logger.info("[Prediction] Unified model not found at %s — using trend fallback", _UNIFIED_MODEL_PATH)
            return None, None, None

        try:
            try:
                import tensorflow as tf  # type: ignore[import]
                PredictionService._model = tf.keras.models.load_model(str(_UNIFIED_MODEL_PATH))
            except ImportError:
                import keras  # type: ignore[import]
                PredictionService._model = keras.models.load_model(str(_UNIFIED_MODEL_PATH))
            logger.info("[Prediction] Loaded unified model from %s", _UNIFIED_MODEL_PATH)
        except Exception as exc:
            logger.warning("[Prediction] Failed to load unified model: %s", exc)
            return None, None, None

        if _UNIFIED_SCALER_PATH.exists():
            try:
                from joblib import load as joblib_load  # type: ignore[import]
                PredictionService._scaler = joblib_load(str(_UNIFIED_SCALER_PATH))
            except Exception as exc:
                logger.warning("[Prediction] Failed to load scaler: %s", exc)

        if _UNIFIED_METADATA_PATH.exists():
            try:
                PredictionService._metadata = json.loads(_UNIFIED_METADATA_PATH.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("[Prediction] Failed to load metadata: %s", exc)

        return PredictionService._model, PredictionService._scaler, PredictionService._metadata

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_daily_series(self, history: list[dict[str, Any]], lookback_days: int) -> list[float]:
        """Resample hourly InfluxDB records to a daily-average AQI series."""
        if not history:
            return []
        try:
            import pandas as pd

            rows = []
            for r in history:
                aqi_val = r.get("aqi")
                ts = r.get("timestamp") or r.get("_time") or r.get("time")
                if aqi_val is not None and ts is not None:
                    rows.append({"ts": ts, "aqi": float(aqi_val)})

            if not rows:
                vals = [float(r["aqi"]) for r in history if r.get("aqi") is not None]
                return vals[-lookback_days:]

            df = pd.DataFrame(rows)
            df["ts"] = pd.to_datetime(df["ts"])
            daily = df.set_index("ts").resample("1D")["aqi"].mean().dropna()
            return daily.tolist()[-lookback_days:]
        except Exception as exc:
            logger.warning("[Prediction] Failed to resample daily series: %s", exc)
            vals = [float(r["aqi"]) for r in history if r.get("aqi") is not None]
            return vals[-lookback_days:]

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
