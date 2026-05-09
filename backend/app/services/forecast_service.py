import logging
from datetime import UTC, datetime, timedelta, date
from typing import Any

from app.core.config import get_settings
from app.integrations.live_aqi_factory import get_live_aqi_adapter
from app.models.forecast_log import ForecastLog
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.repositories.forecast_repository import ForecastRepository
from app.utils.enums import ForecastSourceType
from app.utils.validators import aqi_to_category

logger = logging.getLogger(__name__)

# Horizons used when reading WAQI daily forecast from InfluxDB
_WAQI_HORIZONS = [6, 24, 48, 72]


class ForecastService:
    def __init__(
        self,
        forecast_repository: ForecastRepository,
        timeseries_repository: AQITimeSeriesRepository | None = None,
        live_aqi_adapter: Any | None = None,
    ) -> None:
        self.forecast_repository = forecast_repository
        self.timeseries_repository = timeseries_repository
        self.live_aqi_adapter = live_aqi_adapter if live_aqi_adapter is not None else get_live_aqi_adapter()
        self.settings = get_settings()
        self.forecast_horizons = self._parse_horizons(self.settings.forecast_horizons)

    def generate_current_summary(self, user_id: Any, location_id: Any, city: str | None = None) -> list[dict]:
        """Return ForecastHorizonPoint dicts for the current forecast.

        Priority:
        1. Recent WAQI forecast cached in InfluxDB (written within last 12 h)
        2. ML model predictions already in InfluxDB
        3. Fetch fresh from WAQI, store in InfluxDB, return immediately
        """
        _ = (user_id, location_id)
        if city and self.timeseries_repository is not None:
            # 1. WAQI forecast cached in InfluxDB
            waqi_rows = self.timeseries_repository.read_latest_predictions_for_city(
                city=city,
                horizons=_WAQI_HORIZONS,
                source="waqi",
                lookback_hours=12,
            )
            if waqi_rows:
                normalized = self._normalize_prediction_rows(waqi_rows)
                if normalized:
                    logger.info("[Forecast] Returning %d WAQI horizon(s) from InfluxDB for city=%s", len(normalized), city)
                    return normalized

            # 2. ML model predictions
            model_rows = self.timeseries_repository.read_latest_predictions_for_city(
                city=city,
                horizons=self.forecast_horizons,
                source="model",
            )
            if model_rows:
                normalized = self._normalize_prediction_rows(model_rows)
                if normalized:
                    return normalized

        # 3. Fetch fresh from WAQI
        if city:
            return self._fetch_and_store_waqi_forecast(city)

        return []

    def _fetch_and_store_waqi_forecast(self, city: str) -> list[dict]:
        """Fetch WAQI daily forecast for city, persist to InfluxDB, return horizon dicts."""
        if not hasattr(self.live_aqi_adapter, "fetch_city_full"):
            return []
        try:
            _, forecasts = self.live_aqi_adapter.fetch_city_full(city)
        except Exception as exc:
            logger.warning("[Forecast] fetch_city_full failed for city=%s: %s", city, exc)
            return []

        if not forecasts:
            logger.warning("[Forecast] No forecast days returned by WAQI for city=%s", city)
            return []

        if self.timeseries_repository is not None:
            try:
                written = self.timeseries_repository.write_waqi_forecast_days(city=city, forecasts=forecasts)
                logger.info("[Forecast] Stored %d WAQI forecast day(s) for city=%s", written, city)
            except Exception as exc:
                logger.warning("[Forecast] InfluxDB write failed for city=%s: %s", city, exc)

        horizons = self._waqi_forecasts_to_horizons(forecasts)
        logger.info("[Forecast] Returning %d live WAQI horizon(s) for city=%s", len(horizons), city)
        return horizons

    @staticmethod
    def _waqi_forecasts_to_horizons(forecasts: list[Any]) -> list[dict]:
        """Map WAQIDailyForecast list → ForecastHorizonPoint-compatible dicts."""
        today = datetime.now(tz=UTC).date()
        output: list[dict] = []
        for f in forecasts:
            try:
                forecast_date = date.fromisoformat(f.day)
            except (ValueError, AttributeError, TypeError):
                continue
            day_offset = (forecast_date - today).days
            horizon_hours = max(6, day_offset * 24)
            predicted_aqi = f.avg_pm25 if f.avg_pm25 is not None else f.avg_pm10
            if predicted_aqi is None:
                continue
            predicted_aqi = min(float(predicted_aqi), 500.0)
            try:
                category = aqi_to_category(predicted_aqi)
            except Exception:
                continue
            output.append({
                "horizon_hours": horizon_hours,
                "predicted_aqi": round(predicted_aqi, 1),
                "category": category,
            })
        output.sort(key=lambda x: x["horizon_hours"])
        return output

    def generate_weekly_summary(self, location_id: Any, city: str | None = None) -> list[dict]:
        _ = location_id
        horizons = self.generate_current_summary(user_id=None, location_id=None, city=city)
        if not horizons:
            return []

        base_value = sum(item["predicted_aqi"] for item in horizons) / len(horizons)
        daily = []
        names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for index, name in enumerate(names):
            drift = (index - 2) * 2.5
            predicted = max(0.0, base_value + drift)
            previous = daily[-1]["avg_aqi"] if daily else predicted
            trend = "up" if predicted - previous > 6 else "down" if previous - predicted > 6 else "steady"
            daily.append(
                {
                    "day": name,
                    "avg_aqi": round(predicted, 1),
                    "category": aqi_to_category(predicted),
                    "trend": trend,
                }
            )
        return daily

    def best_window(self, city: str | None = None) -> dict:
        """Find the day with the lowest forecast AQI in the next 3 days.

        Uses WAQI daily min_pm25 for the cleanest air window. Falls back to
        avg_pm25 / model predictions if min values are unavailable.
        """
        if city and self.timeseries_repository is not None:
            # Try WAQI forecast from InfluxDB first (next 3 days: 24 h, 48 h, 72 h)
            predictions = self.timeseries_repository.read_latest_predictions_for_city(
                city=city,
                horizons=_WAQI_HORIZONS,
                source="waqi",
                lookback_hours=12,
            )
            if not predictions:
                # Fall back to model predictions
                predictions = self.timeseries_repository.read_latest_predictions_for_city(
                    city=city,
                    horizons=[4, 6, 12, 24],
                    source="model",
                )
            if predictions:
                return self._predictions_to_best_window(predictions)

        # Fetch fresh WAQI forecast and find best window
        if city:
            horizons = self._fetch_and_store_waqi_forecast(city)
            if horizons:
                best = min(horizons, key=lambda x: x["predicted_aqi"])
                target_time = datetime.now(tz=UTC) + timedelta(hours=best["horizon_hours"])
                return {
                    "date": target_time.date().isoformat(),
                    "start_time": (target_time - timedelta(minutes=45)).strftime("%H:%M"),
                    "end_time": (target_time + timedelta(minutes=45)).strftime("%H:%M"),
                    "expected_aqi": best["predicted_aqi"],
                }

        # Static fallback
        return {
            "date": datetime.now(tz=UTC).date().isoformat(),
            "start_time": "07:00",
            "end_time": "08:30",
            "expected_aqi": 124.0,
        }

    @staticmethod
    def _predictions_to_best_window(predictions: list[dict[str, Any]]) -> dict:
        """From a list of prediction rows, return the best outdoor window dict."""
        # Prefer min_pm25 (actual minimum AQI for the day) over predicted_aqi (avg)
        def sort_key(row: dict[str, Any]) -> float:
            min_val = row.get("min_pm25")
            if min_val is not None:
                return float(min_val)
            return float(row.get("predicted_aqi") or 999)

        best = min(predictions, key=sort_key)
        try:
            horizon = int(best.get("forecast_horizon") or 0)
        except (TypeError, ValueError):
            horizon = 0
        target_time = datetime.now(tz=UTC) + timedelta(hours=horizon)
        expected_aqi = float(best.get("min_pm25") or best.get("predicted_aqi") or 0)
        return {
            "date": target_time.date().isoformat(),
            "start_time": (target_time - timedelta(minutes=45)).strftime("%H:%M"),
            "end_time": (target_time + timedelta(minutes=45)).strftime("%H:%M"),
            "expected_aqi": round(expected_aqi, 1),
        }

    @staticmethod
    def _parse_horizons(value: str) -> list[int]:
        parsed: list[int] = []
        for item in value.split(","):
            text = item.strip()
            if not text:
                continue
            try:
                horizon = int(text)
            except ValueError:
                continue
            if horizon > 0:
                parsed.append(horizon)
        return parsed or [4, 6, 12, 24]

    @staticmethod
    def _normalize_prediction_rows(rows: list[dict[str, Any]]) -> list[dict]:
        output: list[dict] = []
        for row in rows:
            horizon_raw = row.get("forecast_horizon")
            predicted_raw = row.get("predicted_aqi")
            if horizon_raw is None or predicted_raw is None:
                continue
            try:
                horizon = int(horizon_raw)
                predicted_aqi = float(predicted_raw)
            except (TypeError, ValueError):
                continue
            category_raw = row.get("predicted_category")
            if isinstance(category_raw, str) and category_raw.strip():
                category = category_raw.strip()
            else:
                category = aqi_to_category(predicted_aqi)
            output.append(
                {
                    "horizon_hours": horizon,
                    "predicted_aqi": predicted_aqi,
                    "category": category,
                }
            )
        output.sort(key=lambda item: item["horizon_hours"])
        return output
