from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd

from shared.constants import MAX_POLLUTANT_VALUES, POLLUTANT_FIELDS

FeatureMode = Literal["univariate", "multivariate"]
MissingStrategy = Literal["ffill_then_interp", "interpolate_only", "forward_fill_only"]


@dataclass(slots=True)
class KagglePreprocessConfig:
    resample_frequency: str = "1h"
    missing_strategy: MissingStrategy = "ffill_then_interp"
    short_gap_limit: int = 2
    clip_aqi_upper: float = 500.0
    keep_long_gap_missing: bool = True


@dataclass(slots=True)
class KagglePreprocessSummary:
    input_rows: int
    valid_timestamp_rows: int
    deduplicated_rows: int
    continuity_gap_hours: int
    output_rows: int
    dropped_rows: int
    imputed_rows: int
    feature_mode: FeatureMode
    output_columns: list[str]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class KagglePreprocessor:
    """Prepare historical AQI records into training-ready hourly feature series."""

    def __init__(self, config: KagglePreprocessConfig | None = None) -> None:
        self.config = config or KagglePreprocessConfig()

    def preprocess(
        self,
        df: pd.DataFrame,
        *,
        feature_mode: FeatureMode = "univariate",
    ) -> tuple[pd.DataFrame, KagglePreprocessSummary]:
        if df.empty:
            summary = KagglePreprocessSummary(
                input_rows=0,
                valid_timestamp_rows=0,
                deduplicated_rows=0,
                continuity_gap_hours=0,
                output_rows=0,
                dropped_rows=0,
                imputed_rows=0,
                feature_mode=feature_mode,
                output_columns=[],
            )
            return pd.DataFrame(), summary

        frame = df.copy()
        frame["observed_at"] = pd.to_datetime(frame["observed_at"], utc=True, errors="coerce").dt.floor("h")
        input_rows = len(frame)
        frame = frame[frame["observed_at"].notna()].copy()
        valid_timestamp_rows = len(frame)

        numeric_columns = ["aqi", *POLLUTANT_FIELDS]
        for column in numeric_columns:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
            else:
                frame[column] = pd.NA

        frame["aqi"] = frame["aqi"].where(frame["aqi"] >= 0)
        frame["aqi"] = frame["aqi"].clip(upper=self.config.clip_aqi_upper)

        for pollutant in POLLUTANT_FIELDS:
            max_allowed = MAX_POLLUTANT_VALUES[pollutant]
            frame[pollutant] = frame[pollutant].where(frame[pollutant] >= 0)
            frame[pollutant] = frame[pollutant].where(frame[pollutant] <= max_allowed)

        dedupe_subset = ["observed_at"]
        if "station_id" in frame.columns:
            dedupe_subset = ["station_id", "observed_at"]
        frame = frame.sort_values("observed_at").drop_duplicates(subset=dedupe_subset, keep="last")
        deduplicated_rows = len(frame)

        # Convert potentially multi-station city records to a single city-hour series.
        hourly = (
            frame.groupby("observed_at", as_index=False)[numeric_columns]
            .mean(numeric_only=True)
            .sort_values("observed_at")
        )

        if hourly.empty:
            summary = KagglePreprocessSummary(
                input_rows=input_rows,
                valid_timestamp_rows=valid_timestamp_rows,
                deduplicated_rows=deduplicated_rows,
                continuity_gap_hours=0,
                output_rows=0,
                dropped_rows=0,
                imputed_rows=0,
                feature_mode=feature_mode,
                output_columns=[],
            )
            return hourly, summary

        continuity_gap_hours = _continuity_gaps(hourly["observed_at"])

        hourly = hourly.set_index("observed_at").resample(self.config.resample_frequency).mean()
        missing_mask = hourly["aqi"].isna()

        hourly["aqi"] = self._impute_series(hourly["aqi"])
        imputed_mask = missing_mask & hourly["aqi"].notna()

        if feature_mode == "multivariate":
            for pollutant in POLLUTANT_FIELDS:
                hourly[pollutant] = self._impute_series(hourly[pollutant])

        if not self.config.keep_long_gap_missing:
            hourly["aqi"] = hourly["aqi"].ffill().bfill()
            if feature_mode == "multivariate":
                for pollutant in POLLUTANT_FIELDS:
                    hourly[pollutant] = hourly[pollutant].ffill().bfill()

        hourly["missing_flag"] = missing_mask.astype(int)
        hourly["imputed_flag"] = imputed_mask.astype(int)

        hourly = hourly.reset_index().sort_values("observed_at")
        dropped_rows = int(hourly["aqi"].isna().sum())
        hourly = hourly[hourly["aqi"].notna()].copy()

        # Temporal + lag/rolling features for LSTM and fallback models.
        hourly["hour_of_day"] = hourly["observed_at"].dt.hour
        hourly["day_of_week"] = hourly["observed_at"].dt.dayofweek
        hourly["is_weekend"] = (hourly["day_of_week"] >= 5).astype(int)
        hourly["rolling_avg_3h"] = hourly["aqi"].rolling(3, min_periods=1).mean()
        hourly["rolling_avg_6h"] = hourly["aqi"].rolling(6, min_periods=1).mean()
        hourly["rolling_avg_12h"] = hourly["aqi"].rolling(12, min_periods=1).mean()
        hourly["lag_1"] = hourly["aqi"].shift(1)
        hourly["lag_3"] = hourly["aqi"].shift(3)
        hourly["lag_6"] = hourly["aqi"].shift(6)
        hourly["lag_12"] = hourly["aqi"].shift(12)
        hourly["lag_24"] = hourly["aqi"].shift(24)

        if feature_mode == "univariate":
            keep_cols = [
                "observed_at",
                "aqi",
                "missing_flag",
                "imputed_flag",
                "hour_of_day",
                "day_of_week",
                "is_weekend",
                "rolling_avg_3h",
                "rolling_avg_6h",
                "rolling_avg_12h",
                "lag_1",
                "lag_3",
                "lag_6",
                "lag_12",
                "lag_24",
            ]
            hourly = hourly[keep_cols]
        else:
            ordered = [
                "observed_at",
                "aqi",
                *POLLUTANT_FIELDS,
                "missing_flag",
                "imputed_flag",
                "hour_of_day",
                "day_of_week",
                "is_weekend",
                "rolling_avg_3h",
                "rolling_avg_6h",
                "rolling_avg_12h",
                "lag_1",
                "lag_3",
                "lag_6",
                "lag_12",
                "lag_24",
            ]
            keep_cols = [column for column in ordered if column in hourly.columns]
            hourly = hourly[keep_cols]

        summary = KagglePreprocessSummary(
            input_rows=input_rows,
            valid_timestamp_rows=valid_timestamp_rows,
            deduplicated_rows=deduplicated_rows,
            continuity_gap_hours=continuity_gap_hours,
            output_rows=len(hourly),
            dropped_rows=dropped_rows,
            imputed_rows=int(hourly["imputed_flag"].sum()) if "imputed_flag" in hourly.columns else 0,
            feature_mode=feature_mode,
            output_columns=list(hourly.columns),
        )
        return hourly.reset_index(drop=True), summary

    def _impute_series(self, series: pd.Series) -> pd.Series:
        filled = series.copy()
        strategy = self.config.missing_strategy
        limit = self.config.short_gap_limit

        if strategy in {"ffill_then_interp", "forward_fill_only"}:
            filled = filled.ffill(limit=limit)
        if strategy in {"ffill_then_interp", "interpolate_only"}:
            filled = filled.interpolate(method="time", limit=limit, limit_direction="both")

        return filled


def _continuity_gaps(observed_series: pd.Series) -> int:
    if observed_series.empty:
        return 0
    start_at = observed_series.min()
    end_at = observed_series.max()
    if pd.isna(start_at) or pd.isna(end_at):
        return 0
    expected = int((end_at - start_at).total_seconds() // 3600) + 1
    return max(0, expected - int(observed_series.nunique()))
