from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_db_user, get_forecast_service, get_location_service
from app.models.user import User
from app.schemas.forecast import (
    BestWindowResponse,
    ForecastCurrentResponse,
    ForecastGenerateDemoResponse,
    ForecastHorizonPoint,
    WeeklyForecastDay,
    WeeklyForecastResponse,
)
from app.services.forecast_service import ForecastService
from app.services.location_service import LocationService

router = APIRouter(prefix="/forecasts", tags=["forecasts"])


def _resolve_location_id(current_user: User, requested_location_id: UUID | None, location_service: LocationService):
    if requested_location_id:
        return location_service.get_location(current_user.id, requested_location_id).id
    primary = location_service.get_primary_location(current_user.id)
    return primary.id if primary else None


@router.get("/current", response_model=ForecastCurrentResponse)
def get_current_forecast(
    location_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> ForecastCurrentResponse:
    resolved_location_id = _resolve_location_id(current_user, location_id, location_service)
    horizons = forecast_service.generate_current_summary(user_id=current_user.id, location_id=resolved_location_id)
    return ForecastCurrentResponse(
        location_id=resolved_location_id,
        generated_at=datetime.now(tz=UTC),
        horizons=[ForecastHorizonPoint(**item) for item in horizons],
    )


@router.get("/weekly", response_model=WeeklyForecastResponse)
def get_weekly_forecast(
    location_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> WeeklyForecastResponse:
    resolved_location_id = _resolve_location_id(current_user, location_id, location_service)
    days = forecast_service.generate_weekly_summary(location_id=resolved_location_id)
    return WeeklyForecastResponse(
        location_id=resolved_location_id,
        generated_at=datetime.now(tz=UTC),
        days=[WeeklyForecastDay(**item) for item in days],
    )


@router.get("/best-window", response_model=BestWindowResponse)
def get_best_window(
    location_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> BestWindowResponse:
    resolved_location_id = _resolve_location_id(current_user, location_id, location_service)
    window = forecast_service.best_window()
    return BestWindowResponse(location_id=resolved_location_id, **window)


@router.post("/generate-demo", response_model=ForecastGenerateDemoResponse)
def generate_demo_forecasts(
    location_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> ForecastGenerateDemoResponse:
    resolved_location_id = _resolve_location_id(current_user, location_id, location_service)
    saved = forecast_service.generate_demo_logs(user_id=current_user.id, location_id=resolved_location_id)
    return ForecastGenerateDemoResponse(generated=True, location_id=resolved_location_id, saved_records=saved)
