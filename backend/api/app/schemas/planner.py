from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import AQICategory, ActivityType

PlannerTrend = Literal["improving", "stable", "worsening"]
PlannerConfidence = Literal["higher confidence", "moderate confidence", "lower confidence"]


class PlannerLocationSummary(BaseModel):
    location_id: UUID | None = None
    name: str
    city: str
    state: str | None = None
    country: str
    lat: float | None = None
    lon: float | None = None


class PlannerAQIRange(BaseModel):
    min: float = Field(ge=0)
    max: float = Field(ge=0)


class PlannerBestOutdoorWindow(BaseModel):
    start: str | None = None
    end: str | None = None
    label: str
    confidence_label: PlannerConfidence


class PlannerActivitySuitability(BaseModel):
    activity_type: ActivityType
    suitable: bool
    caution_level: str
    note: str
    mask_advised: bool
    avoid_outdoor: bool


class PlannerDayPlan(BaseModel):
    date: str
    day_name: str
    representative_aqi: float = Field(ge=0)
    aqi_range: PlannerAQIRange
    category: AQICategory
    trend: PlannerTrend
    confidence_label: PlannerConfidence
    planning_hint: str
    best_outdoor_window: PlannerBestOutdoorWindow | None = None
    activities: list[PlannerActivitySuitability]


class PlannerWeekSummary(BaseModel):
    overall_outlook: str
    best_days: list[str]
    caution_days: list[str]
    summary_text: str
    worst_day: str | None = None


class PlannerWatchSummary(BaseModel):
    title: str
    lines: list[str]


class WeeklyPlannerResponse(BaseModel):
    location: PlannerLocationSummary
    generated_at: datetime
    week_summary: PlannerWeekSummary
    days: list[PlannerDayPlan]
    watch_summary: PlannerWatchSummary


class PlannerBestDaysResponse(BaseModel):
    location_id: UUID | None = None
    generated_at: datetime
    overall_outlook: str
    best_days: list[str]
    caution_days: list[str]
    worst_day: str | None = None


class PlannerActivityDay(BaseModel):
    date: str
    day_name: str
    category: AQICategory
    representative_aqi: float = Field(ge=0)
    confidence_label: PlannerConfidence
    best_outdoor_window: PlannerBestOutdoorWindow | None = None
    suitable: bool
    caution_level: str
    note: str


class PlannerActivityResponse(BaseModel):
    location_id: UUID | None = None
    activity_type: ActivityType
    generated_at: datetime
    days: list[PlannerActivityDay]


class PlannerGenerateDemoRequest(BaseModel):
    scenario: Literal["good", "mixed", "poor"] = "mixed"


class PlannerGenerateDemoResponse(BaseModel):
    scenario: Literal["good", "mixed", "poor"]
    planner: WeeklyPlannerResponse
