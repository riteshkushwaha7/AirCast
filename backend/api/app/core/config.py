from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AirWise API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    postgres_uri: str = "postgresql+psycopg2://airwise:airwise123@localhost:5432/airwise"
    postgres_echo: bool = False

    influx_url: str = "http://localhost:8086"
    influx_token: str = "dev-influx-token"
    influx_org: str = "airwise"
    influx_bucket: str = "aqi_raw"

    firebase_project_id: str | None = None
    firebase_client_email: str | None = None
    firebase_private_key: str | None = None
    allow_mock_auth: bool = True

    fcm_enabled: bool = False
    fcm_dry_run: bool = True

    default_country: str = "India"
    default_timezone: str = "Asia/Kolkata"

    default_threshold_aqi: int = Field(default=150, ge=50, le=500)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
