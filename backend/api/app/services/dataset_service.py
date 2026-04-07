from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import get_settings
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository

settings = get_settings()


class DatasetService:
    """Builds model-ready datasets from processed AQI time-series."""

    def __init__(self, timeseries_repository: AQITimeSeriesRepository) -> None:
        self.timeseries_repository = timeseries_repository

    def build_city_dataset(
        self,
        city: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> pd.DataFrame:
        start_dt, end_dt = self._resolve_window(start_at=start_at, end_at=end_at)
        rows = self.timeseries_repository.read_processed_records(start_at=start_dt, end_at=end_dt, city=city)
        return self._to_dataframe(rows)

    def build_station_dataset(
        self,
        station_id: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> pd.DataFrame:
        start_dt, end_dt = self._resolve_window(start_at=start_at, end_at=end_at)
        rows = self.timeseries_repository.read_processed_records(start_at=start_dt, end_at=end_dt, station_id=station_id)
        return self._to_dataframe(rows)

    def export_training_dataset(self, df: pd.DataFrame, output_path: str) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".parquet":
            try:
                df.to_parquet(path, index=False)
            except Exception:
                fallback = path.with_suffix(".csv")
                df.to_csv(fallback, index=False)
                return str(fallback)
            return str(path)

        df.to_csv(path, index=False)
        return str(path)

    def split_train_validation_test(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if df.empty:
            return {"train": df.copy(), "validation": df.copy(), "test": df.copy()}

        train_ratio = settings.dataset_train_ratio
        val_ratio = settings.dataset_val_ratio
        total_ratio = train_ratio + val_ratio + settings.dataset_test_ratio
        if abs(total_ratio - 1.0) > 0.01:
            train_ratio = 0.7
            val_ratio = 0.15

        total_rows = len(df)
        train_end = int(total_rows * train_ratio)
        val_end = train_end + int(total_rows * val_ratio)

        return {
            "train": df.iloc[:train_end].copy(),
            "validation": df.iloc[train_end:val_end].copy(),
            "test": df.iloc[val_end:].copy(),
        }

    def prepare_sequence_windows(
        self,
        df: pd.DataFrame,
        lookback: int = 24,
        horizons: tuple[int, ...] = (4, 6, 12, 24),
        feature_columns: list[str] | None = None,
        target_column: str = "aqi",
    ) -> tuple[list[list[list[float]]], list[list[float]]]:
        if df.empty:
            return [], []

        columns = feature_columns or [
            "aqi",
            "rolling_avg_3h",
            "rolling_avg_6h",
            "rolling_avg_12h",
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "lag_1",
            "lag_3",
            "lag_6",
            "lag_12",
            "lag_24",
        ]
        available_columns = [column for column in columns if column in df.columns]
        values = df[available_columns].fillna(method="ffill").fillna(method="bfill").to_numpy(dtype=float)
        targets = df[target_column].to_numpy(dtype=float)

        sequences: list[list[list[float]]] = []
        outputs: list[list[float]] = []
        max_horizon = max(horizons)
        for index in range(lookback, len(df) - max_horizon):
            sequence = values[index - lookback : index]
            horizon_targets = [targets[index + horizon] for horizon in horizons]
            sequences.append(sequence.tolist())
            outputs.append(horizon_targets)

        return sequences, outputs

    def dataset_summary(self, df: pd.DataFrame, export_path: str | None = None) -> dict[str, Any]:
        if df.empty:
            return {"row_count": 0, "station_count": 0, "city_count": 0, "columns": [], "export_path": export_path}

        return {
            "row_count": int(len(df)),
            "station_count": int(df["station_id"].nunique()) if "station_id" in df.columns else 0,
            "city_count": int(df["city"].nunique()) if "city" in df.columns else 0,
            "columns": list(df.columns),
            "export_path": export_path,
        }

    def _resolve_window(self, start_at: datetime | None, end_at: datetime | None) -> tuple[datetime, datetime]:
        end_dt = end_at.astimezone(UTC) if end_at else datetime.now(tz=UTC)
        start_dt = start_at.astimezone(UTC) if start_at else end_dt - timedelta(days=30)
        return start_dt, end_dt

    def _to_dataframe(self, rows: list[dict[str, Any]]) -> pd.DataFrame:
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        if "observed_at" in df.columns:
            df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True)
            df = df.sort_values("observed_at")
        return df.reset_index(drop=True)
