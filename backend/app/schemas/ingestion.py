from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.enums import AQICategory
from app.utils.validators import (
    normalize_blank_string,
    validate_latitude,
    validate_longitude,
    validate_optional_non_negative,
)


class NormalizedAQIRecord(BaseModel):
    source: str
    station_id: str | None = None
    station_name: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    observed_at: datetime
    aqi: float | None = None
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    nh3: float | None = None

    model_config = ConfigDict(extra="ignore")

    @field_validator(
        "source",
        "station_id",
        "station_name",
        "city",
        "state",
        "country",
        mode="before",
    )
    @classmethod
    def _normalize_text(cls, value: str | None) -> str | None:
        return normalize_blank_string(value)

    @field_validator("observed_at", mode="before")
    @classmethod
    def _normalize_observed_at(cls, value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            parsed = value
        else:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @field_validator("latitude")
    @classmethod
    def _validate_latitude(cls, value: float | None) -> float | None:
        if value is None:
            return value
        return validate_latitude(value)

    @field_validator("longitude")
    @classmethod
    def _validate_longitude(cls, value: float | None) -> float | None:
        if value is None:
            return value
        return validate_longitude(value)

    @field_validator("aqi", "pm25", "pm10", "no2", "so2", "co", "o3", "nh3")
    @classmethod
    def _validate_non_negative_values(cls, value: float | None) -> float | None:
        return validate_optional_non_negative(value)

    @model_validator(mode="after")
    def _validate_station_or_location(self) -> "NormalizedAQIRecord":
        has_station = bool(self.station_id)
        has_location = bool(self.city) or (self.latitude is not None and self.longitude is not None)
        if not has_station and not has_location:
            raise ValueError("Record must include station_id or a location descriptor")
        if self.aqi is None and all(
            pollutant is None for pollutant in (self.pm25, self.pm10, self.no2, self.so2, self.co, self.o3, self.nh3)
        ):
            raise ValueError("Record must include AQI or at least one pollutant value")
        return self


class ProcessedAQIRecord(BaseModel):
    source: str
    station_id: str
    city: str
    observed_at: datetime
    aqi: float
    rolling_avg_3h: float
    rolling_avg_6h: float
    rolling_avg_12h: float
    lag_1: float | None = None
    lag_3: float | None = None
    lag_6: float | None = None
    lag_12: float | None = None
    lag_24: float | None = None
    hour_of_day: int
    day_of_week: int
    is_weekend: int
    missing_flag: int = Field(ge=0, le=1)
    imputed_flag: int = Field(ge=0, le=1)


class IngestionSummary(BaseModel):
    source: str
    mode: str
    fetched_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    written_count: int
    started_at: datetime
    ended_at: datetime
    invalid_reasons: list[str] = Field(default_factory=list)


class PreprocessingSummary(BaseModel):
    started_at: datetime
    ended_at: datetime
    group_count: int
    input_rows: int
    output_rows: int
    dropped_rows: int
    imputed_rows: int
    write_count: int


class IngestionRunCurrentRequest(BaseModel):
    city: str | None = None
    limit: int = Field(default=500, ge=10, le=5000)


class IngestionBackfillRequest(BaseModel):
    city: str
    days: int = Field(default=30, ge=1, le=730)
    start_at: datetime | None = None
    end_at: datetime | None = None
    limit: int = Field(default=2000, ge=50, le=10000)

    @model_validator(mode="after")
    def _validate_range(self) -> "IngestionBackfillRequest":
        if self.start_at and self.end_at and self.start_at >= self.end_at:
            raise ValueError("start_at must be earlier than end_at")
        return self


class PreprocessingRunRequest(BaseModel):
    city: str | None = None
    station_id: str | None = None
    lookback_hours: int | None = Field(default=None, ge=24, le=24 * 180)


class IngestionSummaryResponse(BaseModel):
    summary: IngestionSummary | None = None


class TrainingDatasetRequest(BaseModel):
    city: str | None = None
    station_id: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    export_path: str | None = None


class ForecastFeaturePoint(BaseModel):
    observed_at: datetime
    aqi: float
    category: AQICategory


class IngestionTriggerResponse(BaseModel):
    message: str
    summary: IngestionSummary


class PreprocessingTriggerResponse(BaseModel):
    message: str
    summary: PreprocessingSummary


class DatasetBuildResponse(BaseModel):
    row_count: int
    station_count: int
    city_count: int
    columns: list[str]
    export_path: str | None = None


class IngestionFilter(BaseModel):
    city: str | None = None
    station_id: str | None = None
    source: str | None = None
    start_at: datetime
    end_at: datetime
    user_id: UUID | None = None
