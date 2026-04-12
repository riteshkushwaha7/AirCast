from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import AQICategory, ActivityType


class ForecastHorizonSnapshot(BaseModel):
    horizon_hours: int
    predicted_aqi: float = Field(ge=0)
    category: AQICategory


class BestWindowSummary(BaseModel):
    start_time: str
    end_time: str
    expected_aqi: float | None = Field(default=None, ge=0)


class RecommendationCurrentResponse(BaseModel):
    location_id: UUID | None = None
    activity_type: ActivityType | None = None
    current_aqi: float = Field(ge=0)
    category: AQICategory
    risk_level: str
    short_status: str
    recommendation_text: str
    confidence_note: str
    mask_advised: bool
    avoid_outdoor: bool
    activity_suitable: bool
    activity_guidance: str
    forecast_horizons: list[ForecastHorizonSnapshot]
    best_window: BestWindowSummary | None = None


class RecommendationCompactResponse(BaseModel):
    short_status: str
    recommendation_text: str
    risk_level: str
    mask_advised: bool
    avoid_outdoor: bool
    activity_suitable: bool


class RecommendationExplainDemoRequest(BaseModel):
    current_aqi: float = Field(ge=0)
    category: AQICategory
    risk_level: str
    recommendation_text: str
    activity_type: ActivityType | None = None


class RecommendationExplainDemoResponse(BaseModel):
    summary: str
