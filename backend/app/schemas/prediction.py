from uuid import UUID

from pydantic import BaseModel, Field


class PredictionRunRequest(BaseModel):
    location_id: UUID


class PredictionHorizonResult(BaseModel):
    horizon_hours: int
    predicted_aqi: float = Field(ge=0)
    category: str
    target_timestamp: str


class PredictionRunResponse(BaseModel):
    location_id: str
    city: str
    generated_at: str
    horizons: list[PredictionHorizonResult]
