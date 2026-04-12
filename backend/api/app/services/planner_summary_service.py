from app.domain.planner_logic import DayScoreInput, identify_caution_days, identify_worst_day, rank_best_days
from app.schemas.planner import PlannerDayPlan, PlannerWatchSummary, PlannerWeekSummary
from app.utils.enums import AQICategory


class PlannerSummaryService:
    def summarize_week(self, days: list[PlannerDayPlan]) -> PlannerWeekSummary:
        score_inputs = [
            DayScoreInput(
                day_name=day.day_name,
                representative_aqi=day.representative_aqi,
                category=day.category,
                confidence_label=day.confidence_label,
                has_best_window=day.best_outdoor_window is not None,
                severe_activity_count=sum(1 for item in day.activities if not item.suitable and item.caution_level in {"high", "severe"}),
            )
            for day in days
        ]

        best_days = rank_best_days(score_inputs, limit=2)
        caution_days = identify_caution_days(score_inputs)
        worst_day = identify_worst_day(score_inputs)
        overall_outlook = self._overall_outlook(days)
        summary_text = self._summary_text(days=days, best_days=best_days, caution_days=caution_days)

        return PlannerWeekSummary(
            overall_outlook=overall_outlook,
            best_days=best_days,
            caution_days=caution_days,
            summary_text=summary_text,
            worst_day=worst_day,
        )

    def build_watch_summary(self, summary: PlannerWeekSummary) -> PlannerWatchSummary:
        best_day_line = f"Best day: {summary.best_days[0]}" if summary.best_days else "No clear best day this week"
        caution_line = (
            f"Caution: {summary.caution_days[0]} may be poor outdoors"
            if summary.caution_days
            else "No major caution day flagged"
        )
        morning_line = "Morning windows are generally safer for short outdoor plans."
        return PlannerWatchSummary(
            title="AirWise weekly outlook",
            lines=[best_day_line, caution_line, morning_line],
        )

    def _overall_outlook(self, days: list[PlannerDayPlan]) -> str:
        if not days:
            return "Weekly outlook unavailable"
        avg_aqi = sum(day.representative_aqi for day in days) / len(days)
        if avg_aqi <= 95:
            return "Generally manageable air quality this week"
        if avg_aqi <= 145:
            return "Mixed air quality this week"
        if avg_aqi <= 190:
            return "Challenging outdoor conditions this week"
        return "Mostly poor air quality this week"

    def _summary_text(
        self,
        *,
        days: list[PlannerDayPlan],
        best_days: list[str],
        caution_days: list[str],
    ) -> str:
        if not days:
            return "Planner data is currently limited."

        improving_count = sum(1 for day in days if day.trend == "improving")
        worsening_count = sum(1 for day in days if day.trend == "worsening")

        trend_sentence = "Conditions may improve later in the week." if improving_count >= worsening_count else "Some days may worsen by afternoon."
        best_day_sentence = (
            f"{best_days[0]} looks better for outdoor activity." if best_days else "No clearly low-risk day is visible right now."
        )
        caution_sentence = (
            f"Use extra caution on {', '.join(caution_days[:2])}."
            if caution_days
            else "Most days look manageable with normal precautions."
        )

        return f"{trend_sentence} {best_day_sentence} {caution_sentence} Morning slots are usually safer for shorter activity."


def has_poor_category(day: PlannerDayPlan) -> bool:
    return day.category in {
        AQICategory.UNHEALTHY,
        AQICategory.VERY_UNHEALTHY,
        AQICategory.HAZARDOUS,
    }
