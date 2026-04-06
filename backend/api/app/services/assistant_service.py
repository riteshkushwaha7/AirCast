from app.schemas.assistant import AssistantExplainRequest, AssistantExplainResponse


class AssistantService:
    def explain(self, payload: AssistantExplainRequest) -> AssistantExplainResponse:
        explanation = (
            f"For {payload.location_label}, AQI is currently {payload.current_aqi:.0f} ({payload.current_category}). "
            f"Recommendation: {payload.recommendation_text} Trend note: {payload.trend_summary}."
        )
        return AssistantExplainResponse(explanation=explanation)
