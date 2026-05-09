from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import AQICategory, ActivityType


class AQIReading(BaseModel):
    timestamp: datetime
    aqi: float = Field(ge=0)
    category: AQICategory
    city: str
    state: str | None = None
    country: str


class AQICurrentResponse(BaseModel):
    location_id: UUID | None = None
    reading: AQIReading


class AQIHistoryPoint(BaseModel):
    timestamp: datetime
    aqi: float = Field(ge=0)


class AQIHistoryResponse(BaseModel):
    location_id: UUID | None = None
    range: str
    points: list[AQIHistoryPoint]


class ForecastHorizonPoint(BaseModel):
    horizon_hours: int
    predicted_aqi: float = Field(ge=0)
    category: AQICategory


class ForecastCurrentResponse(BaseModel):
    location_id: UUID | None = None
    generated_at: datetime
    horizons: list[ForecastHorizonPoint]


class WeeklyForecastDay(BaseModel):
    day: str
    avg_aqi: float = Field(ge=0)
    category: AQICategory
    trend: str


class WeeklyForecastResponse(BaseModel):
    location_id: UUID | None = None
    generated_at: datetime
    days: list[WeeklyForecastDay]


class BestWindowResponse(BaseModel):
    location_id: UUID | None = None
    date: str
    start_time: str
    end_time: str
    expected_aqi: float = Field(ge=0)


class ForecastGenerateDemoResponse(BaseModel):
    generated: bool
    location_id: UUID | None = None
    saved_records: int


class RecommendationResponse(BaseModel):
    location_id: UUID | None = None
    activity_type: ActivityType | None = None
    current_aqi: float = Field(ge=0)
    category: AQICategory
    short_status: str
    recommendation_text: str
    mask_advised: bool
    avoid_outdoor: bool
    risk_level: str
