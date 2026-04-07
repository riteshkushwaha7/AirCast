import logging
from datetime import UTC, datetime, timedelta
from math import isnan
from typing import Any

import pandas as pd

from app.core.config import get_settings
from app.repositories.aqi_timeseries_repository import AQIProcessedRecord, AQITimeSeriesRepository
from app.schemas.ingestion import PreprocessingSummary
from app.services.feature_service import FeatureService

logger = logging.getLogger(__name__)
settings = get_settings()


class PreprocessingService:
    def __init__(
        self,
        timeseries_repository: AQITimeSeriesRepository,
        feature_service: FeatureService | None = None,
    ) -> None:
        self.timeseries_repository = timeseries_repository
        self.feature_service = feature_service or FeatureService()
        self._latest_summary: PreprocessingSummary | None = None

    def run_preprocessing(
        self,
        city: str | None = None,
        station_id: str | None = None,
        lookback_hours: int | None = None,
    ) -> PreprocessingSummary:
        started_at = datetime.now(tz=UTC)
        lookback = lookback_hours or settings.processing_default_lookback_hours
        end_at = datetime.now(tz=UTC)
        start_at = end_at - timedelta(hours=lookback)

        raw_rows = self.timeseries_repository.read_raw_records(
            start_at=start_at,
            end_at=end_at,
            city=city,
            station_id=station_id,
        )
        if not raw_rows:
            summary = PreprocessingSummary(
                started_at=started_at,
                ended_at=datetime.now(tz=UTC),
                group_count=0,
                input_rows=0,
                output_rows=0,
                dropped_rows=0,
                imputed_rows=0,
                write_count=0,
            )
            self._latest_summary = summary
            return summary

        raw_df = pd.DataFrame(raw_rows)
        raw_df["observed_at"] = pd.to_datetime(raw_df["observed_at"], utc=True)

        required_columns = ["source", "station_id", "city", "observed_at", "aqi"]
        for column in required_columns:
            if column not in raw_df.columns:
                raw_df[column] = None

        grouped = raw_df.groupby(["source", "station_id", "city"], dropna=False)
        processed_records: list[AQIProcessedRecord] = []
        output_rows = 0
        dropped_rows = 0
        imputed_rows = 0
        group_count = 0

        for (source, station, city_value), frame in grouped:
            group_count += 1
            prepared, dropped, imputed = self._preprocess_group(frame)
            dropped_rows += dropped
            imputed_rows += imputed

            if prepared.empty:
                continue

            station_id_value = str(station or "unknown")
            city_name = str(city_value or "unknown")
            source_name = str(source or "unknown")

            for row in prepared.to_dict(orient="records"):
                processed_records.append(
                    AQIProcessedRecord(
                        source=source_name,
                        station_id=station_id_value,
                        city=city_name,
                        timestamp=row["observed_at"],
                        aqi=float(row["aqi"]),
                        rolling_avg_3h=float(row["rolling_avg_3h"]),
                        rolling_avg_6h=float(row["rolling_avg_6h"]),
                        rolling_avg_12h=float(row["rolling_avg_12h"]),
                        hour_of_day=int(row["hour_of_day"]),
                        day_of_week=int(row["day_of_week"]),
                        is_weekend=int(row["is_weekend"]),
                        missing_flag=int(row["missing_flag"]),
                        imputed_flag=int(row["imputed_flag"]),
                        lag_1=_to_optional_float(row.get("lag_1")),
                        lag_3=_to_optional_float(row.get("lag_3")),
                        lag_6=_to_optional_float(row.get("lag_6")),
                        lag_12=_to_optional_float(row.get("lag_12")),
                        lag_24=_to_optional_float(row.get("lag_24")),
                    )
                )

            output_rows += len(prepared)

        write_count = self.timeseries_repository.write_processed_records(processed_records)
        summary = PreprocessingSummary(
            started_at=started_at,
            ended_at=datetime.now(tz=UTC),
            group_count=group_count,
            input_rows=len(raw_rows),
            output_rows=output_rows,
            dropped_rows=dropped_rows,
            imputed_rows=imputed_rows,
            write_count=write_count,
        )
        self._latest_summary = summary
        logger.info(
            "Preprocessing completed groups=%s input=%s output=%s dropped=%s imputed=%s written=%s",
            group_count,
            len(raw_rows),
            output_rows,
            dropped_rows,
            imputed_rows,
            write_count,
        )
        return summary

    def get_latest_summary(self) -> PreprocessingSummary | None:
        return self._latest_summary

    def _preprocess_group(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
        prepared = frame.copy()
        prepared["observed_at"] = pd.to_datetime(prepared["observed_at"], utc=True).dt.floor("h")
        prepared = prepared.sort_values("observed_at")
        prepared = prepared.drop_duplicates(subset=["observed_at"], keep="last")
        prepared["aqi"] = pd.to_numeric(prepared["aqi"], errors="coerce")
        prepared["aqi"] = prepared["aqi"].where(prepared["aqi"] >= 0)

        if settings.processing_enable_outlier_clipping:
            prepared["aqi"] = prepared["aqi"].clip(upper=settings.processing_aqi_clip_upper)

        prepared = prepared.set_index("observed_at")
        hourly = prepared[["aqi"]].resample(settings.processing_resample_frequency).mean()

        missing_mask = hourly["aqi"].isna()
        filled = hourly["aqi"].copy()
        gap_limit = settings.processing_short_gap_limit_hours
        strategy = settings.processing_missing_strategy

        if strategy in {"ffill_then_interp", "forward_fill_only"}:
            filled = filled.ffill(limit=gap_limit)
        if strategy in {"ffill_then_interp", "interpolate_only"}:
            filled = filled.interpolate(method="time", limit=gap_limit, limit_direction="both")

        imputed_mask = missing_mask & filled.notna()
        hourly["aqi"] = filled
        hourly["missing_flag"] = missing_mask.astype(int)
        hourly["imputed_flag"] = imputed_mask.astype(int)

        if not settings.processing_long_gap_keep_missing:
            hourly["aqi"] = hourly["aqi"].fillna(method="ffill").fillna(method="bfill")

        with_aqi = hourly.reset_index()
        dropped_rows = int(with_aqi["aqi"].isna().sum())
        with_aqi = with_aqi[with_aqi["aqi"].notna()].copy()
        if with_aqi.empty:
            return with_aqi, dropped_rows, 0

        with_features = self.feature_service.build_features(with_aqi)
        with_features["missing_flag"] = with_features["missing_flag"].astype(int)
        with_features["imputed_flag"] = with_features["imputed_flag"].astype(int)
        imputed_rows = int(with_features["imputed_flag"].sum())

        return with_features, dropped_rows, imputed_rows


def _to_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and isnan(value):
        return None
    return float(value)
