from datetime import UTC, date, datetime, timedelta
from typing import Iterable

from app.domain.activity_planner_rules import evaluate_activity_suitability
from app.domain.aqi_thresholds import aqi_to_category
from app.domain.confidence_labels import confidence_from_horizon
from app.domain.planner_logic import build_planning_hint, derive_trend, estimate_aqi_range
from app.schemas.planner import (
    PlannerActivityDay,
    PlannerActivityResponse,
    PlannerBestDaysResponse,
    PlannerDayPlan,
    PlannerLocationSummary,
    PlannerWeekSummary,
    WeeklyPlannerResponse,
)
from app.services.best_window_service import BestWindowService
from app.services.forecast_service import ForecastService
from app.services.mock_data import SAMPLE_WEEKLY_PLANNER_SCENARIOS
from app.services.planner_summary_service import PlannerSummaryService
from app.utils.enums import ActivityType, HealthProfile, SensitivityLevel


class WeeklyPlannerService:
    def __init__(
        self,
        forecast_service: ForecastService,
        best_window_service: BestWindowService | None = None,
        summary_service: PlannerSummaryService | None = None,
    ) -> None:
        self.forecast_service = forecast_service
        self.best_window_service = best_window_service or BestWindowService()
        self.summary_service = summary_service or PlannerSummaryService()

    def get_weekly_plan(
        self,
        *,
        location,
        health_profile: HealthProfile,
        sensitivity_level: SensitivityLevel,
        activities: list[ActivityType] | None = None,
        scenario: str | None = None,
    ) -> WeeklyPlannerResponse:
        base_series = self._get_base_series(location_id=getattr(location, "id", None), scenario=scenario)
        near_term_window = self.forecast_service.best_window()

        days: list[PlannerDayPlan] = []
        previous_aqi: float | None = None
        today = date.today()

        for index, representative_aqi in enumerate(base_series[:7]):
            trend = derive_trend(previous_aqi, representative_aqi)
            category = aqi_to_category(representative_aqi)
            min_aqi, max_aqi = estimate_aqi_range(representative_aqi, index)

            volatility = abs(representative_aqi - previous_aqi) if previous_aqi is not None else 8.0
            confidence = confidence_from_horizon(
                day_index=index,
                volatility=volatility,
                data_completeness=0.96 if index <= 1 else 0.85,
                model_quality=0.82 if index <= 2 else 0.74,
            )

            best_window = self.best_window_service.build_best_window(
                day_index=index,
                category=category,
                strong_window=near_term_window if index == 0 else None,
            )
            activity_plans = evaluate_activity_suitability(
                representative_aqi=representative_aqi,
                peak_aqi=max_aqi,
                category=category,
                health_profile=health_profile,
                sensitivity_level=sensitivity_level,
                activities=activities,
            )
            day_date = today + timedelta(days=index)
            planning_hint = build_planning_hint(
                category=category,
                trend=trend,
                has_best_window=best_window is not None,
            )

            days.append(
                PlannerDayPlan(
                    date=day_date.isoformat(),
                    day_name=day_date.strftime("%A"),
                    representative_aqi=round(representative_aqi, 1),
                    aqi_range={"min": min_aqi, "max": max_aqi},
                    category=category,
                    trend=trend,
                    confidence_label=confidence,
                    planning_hint=planning_hint,
                    best_outdoor_window=best_window,
                    activities=[
                        {
                            "activity_type": item.activity_type,
                            "suitable": item.suitable,
                            "caution_level": item.caution_level,
                            "note": item.note,
                            "mask_advised": item.mask_advised,
                            "avoid_outdoor": item.avoid_outdoor,
                        }
                        for item in activity_plans
                    ],
                )
            )
            previous_aqi = representative_aqi

        summary = self.summary_service.summarize_week(days)
        return WeeklyPlannerResponse(
            location=self._location_summary(location, scenario=scenario),
            generated_at=datetime.now(tz=UTC),
            week_summary=summary,
            days=days,
            watch_summary=self.summary_service.build_watch_summary(summary),
        )

    def get_best_days(
        self,
        *,
        location,
        health_profile: HealthProfile,
        sensitivity_level: SensitivityLevel,
        activities: list[ActivityType] | None = None,
    ) -> PlannerBestDaysResponse:
        planner = self.get_weekly_plan(
            location=location,
            health_profile=health_profile,
            sensitivity_level=sensitivity_level,
            activities=activities,
        )
        summary: PlannerWeekSummary = planner.week_summary
        return PlannerBestDaysResponse(
            location_id=planner.location.location_id,
            generated_at=planner.generated_at,
            overall_outlook=summary.overall_outlook,
            best_days=summary.best_days,
            caution_days=summary.caution_days,
            worst_day=summary.worst_day,
        )

    def get_activity_outlook(
        self,
        *,
        location,
        health_profile: HealthProfile,
        sensitivity_level: SensitivityLevel,
        activity_type: ActivityType,
    ) -> PlannerActivityResponse:
        planner = self.get_weekly_plan(
            location=location,
            health_profile=health_profile,
            sensitivity_level=sensitivity_level,
            activities=[activity_type],
        )
        activity_days: list[PlannerActivityDay] = []
        for day in planner.days:
            if not day.activities:
                continue
            activity = day.activities[0]
            activity_days.append(
                PlannerActivityDay(
                    date=day.date,
                    day_name=day.day_name,
                    category=day.category,
                    representative_aqi=day.representative_aqi,
                    confidence_label=day.confidence_label,
                    best_outdoor_window=day.best_outdoor_window,
                    suitable=activity.suitable,
                    caution_level=activity.caution_level,
                    note=activity.note,
                )
            )
        return PlannerActivityResponse(
            location_id=planner.location.location_id,
            activity_type=activity_type,
            generated_at=planner.generated_at,
            days=activity_days,
        )

    def generate_demo(
        self,
        *,
        scenario: str,
        health_profile: HealthProfile = HealthProfile.GENERAL,
        sensitivity_level: SensitivityLevel = SensitivityLevel.NORMAL,
        activities: list[ActivityType] | None = None,
    ) -> WeeklyPlannerResponse:
        return self.get_weekly_plan(
            location=None,
            health_profile=health_profile,
            sensitivity_level=sensitivity_level,
            activities=activities,
            scenario=scenario,
        )

    @staticmethod
    def coerce_activity_types(values: Iterable[str | ActivityType] | None) -> list[ActivityType]:
        if values is None:
            return []
        output: list[ActivityType] = []
        for value in values:
            if isinstance(value, ActivityType):
                output.append(value)
                continue
            try:
                output.append(ActivityType(value))
            except ValueError:
                continue
        return output

    def _get_base_series(self, *, location_id, scenario: str | None) -> list[float]:
        if scenario and scenario in SAMPLE_WEEKLY_PLANNER_SCENARIOS:
            return list(SAMPLE_WEEKLY_PLANNER_SCENARIOS[scenario])

        weekly = self.forecast_service.generate_weekly_summary(location_id=location_id)
        values = [float(item["avg_aqi"]) for item in weekly if item.get("avg_aqi") is not None]
        if len(values) >= 7:
            return values[:7]

        fallback = list(SAMPLE_WEEKLY_PLANNER_SCENARIOS["mixed"])
        merged = values + fallback[len(values) :]
        return merged[:7]

    @staticmethod
    def _location_summary(location, *, scenario: str | None) -> PlannerLocationSummary:
        if location is not None:
            return PlannerLocationSummary(
                location_id=location.id,
                name=f"{location.city}{', ' + location.state if location.state else ''}",
                city=location.city,
                state=location.state,
                country=location.country,
                lat=location.latitude,
                lon=location.longitude,
            )
        fallback_city = {
            "good": "Bengaluru",
            "mixed": "Delhi",
            "poor": "Noida",
        }.get(scenario or "mixed", "Delhi")
        return PlannerLocationSummary(
            location_id=None,
            name=fallback_city,
            city=fallback_city,
            state=None,
            country="India",
            lat=None,
            lon=None,
        )
