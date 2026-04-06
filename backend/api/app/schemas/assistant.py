from pydantic import BaseModel, Field


class AssistantExplainRequest(BaseModel):
    location_label: str = Field(min_length=1, max_length=128)
    current_aqi: float = Field(ge=0)
    current_category: str
    recommendation_text: str
    trend_summary: str


class AssistantExplainResponse(BaseModel):
    explanation: str
    disclaimer: str = "AirCast Assistant explains model outputs and does not generate AQI predictions."
