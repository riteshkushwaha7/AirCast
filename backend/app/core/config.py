from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AirWise API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    postgres_uri: str = "postgresql+psycopg2://airwise:airwise123@localhost:5432/airwise"
    postgres_echo: bool = False

    influx_url: str = "http://localhost:8086"
    influx_token: str = "dev-influx-token"
    influx_org: str = "airwise"
    influx_bucket: str = "airwise_timeseries"
    influx_raw_measurement: str = "aqi_raw"
    influx_processed_measurement: str = "aqi_processed"
    influx_predictions_measurement: str = "aqi_predictions"
    influx_model_metrics_measurement: str = "model_metrics"
    influx_pollutant_measurement: str = "pollutant_raw"

    firebase_project_id: str | None = None
    firebase_client_email: str | None = None
    firebase_private_key: str | None = None
    allow_mock_auth: bool = False
    source_mock_mode: bool = False

    fcm_enabled: bool = False
    fcm_dry_run: bool = True

    default_country: str = "India"
    default_timezone: str = "Asia/Kolkata"

    default_threshold_aqi: int = Field(default=150, ge=50, le=500)

    cpcb_base_url: str = "https://api.example.cpcb.gov.in"
    cpcb_timeout_seconds: int = Field(default=20, ge=2, le=120)
    cpcb_default_limit: int = Field(default=500, ge=50, le=5000)

    live_aqi_provider: Literal["cpcb", "waqi"] = "waqi"
    live_aqi_base_url: str = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
    live_aqi_api_key: str | None = None
    live_aqi_timeout: int = Field(default=30, ge=2, le=120)
    live_aqi_default_limit: int = Field(default=1000, ge=10, le=5000)

    waqi_api_token: str | None = None
    waqi_timeout_seconds: int = Field(default=20, ge=2, le=120)
    waqi_default_cities: str = "gurugram,delhi,mumbai,bangalore,hyderabad,chennai,kolkata,pune,ahmedabad,jaipur"

    weather_base_url: str = "https://weather.example.com"
    weather_timeout_seconds: int = Field(default=10, ge=2, le=60)

    processing_resample_frequency: str = "1h"
    processing_default_lookback_hours: int = Field(default=336, ge=24, le=24 * 90)
    processing_short_gap_limit_hours: int = Field(default=2, ge=1, le=24)
    processing_enable_outlier_clipping: bool = True
    processing_aqi_clip_upper: int = Field(default=500, ge=100, le=2000)
    processing_missing_strategy: Literal["ffill_then_interp", "interpolate_only", "forward_fill_only"] = "ffill_then_interp"
    processing_long_gap_keep_missing: bool = True

    dataset_train_ratio: float = Field(default=0.7, ge=0.5, le=0.9)
    dataset_val_ratio: float = Field(default=0.15, ge=0.05, le=0.4)
    dataset_test_ratio: float = Field(default=0.15, ge=0.05, le=0.4)

    default_train_city: str = "Delhi"
    train_target_column: str = "aqi"
    lookback_hours: int = Field(default=24, ge=6, le=240)
    forecast_horizons: str = "4,6,12,24"
    lstm_model_path: str = "models/lstm_aqi.keras"
    lstm_models_dir: str = "models"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("debug", mode="before")
    @classmethod
    def _normalize_debug(cls, value: bool | str) -> bool:
        if isinstance(value, bool):
            return value
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
            return False
        return True

    @field_validator("postgres_uri", mode="before")
    @classmethod
    def _normalize_postgres_uri(cls, value: str) -> str:
        normalized = value.strip()
        if normalized.startswith("postgresql://"):
            return normalized.replace("postgresql://", "postgresql+psycopg2://", 1)
        if normalized.startswith("postgres://"):
            return normalized.replace("postgres://", "postgresql+psycopg2://", 1)
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
