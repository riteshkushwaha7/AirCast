from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_aqi_service, get_current_db_user, get_location_service
from app.models.user import User
from app.schemas.forecast import AQICurrentResponse, AQIHistoryPoint, AQIHistoryResponse, AQIReading
from app.services.aqi_service import AQIService
from app.services.location_service import LocationService
from app.utils.validators import validate_latitude, validate_longitude

router = APIRouter(prefix="/aqi", tags=["aqi"])


def _parse_range_hours(range_value: str) -> int:
    value = range_value.strip().lower().replace(" ", "")
    if not value.endswith("h"):
        return 24
    try:
        hours = int(value[:-1])
    except ValueError:
        return 24
    return max(1, min(hours, 168))


@router.get("/current", response_model=AQICurrentResponse)
def get_current_aqi(
    location_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    aqi_service: AQIService = Depends(get_aqi_service),
) -> AQICurrentResponse:
    location = location_service.get_location(current_user.id, location_id) if location_id else location_service.get_primary_location(current_user.id)
    if location:
        reading = aqi_service.get_current_by_city(city=location.city, state=location.state, country=location.country)
        return AQICurrentResponse(location_id=location.id, reading=AQIReading(**reading))

    fallback = aqi_service.get_current_fallback()
    return AQICurrentResponse(location_id=None, reading=AQIReading(**fallback))


@router.get("/current/by-coordinates", response_model=AQICurrentResponse)
def get_current_by_coordinates(
    lat: float = Query(...),
    lon: float = Query(...),
    _: User = Depends(get_current_db_user),
    aqi_service: AQIService = Depends(get_aqi_service),
) -> AQICurrentResponse:
    validate_latitude(lat)
    validate_longitude(lon)
    reading = aqi_service.get_current_fallback()
    return AQICurrentResponse(location_id=None, reading=AQIReading(**reading))


@router.get("/history", response_model=AQIHistoryResponse)
def get_aqi_history(
    location_id: UUID | None = Query(default=None),
    range: str = Query(default="24h"),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    aqi_service: AQIService = Depends(get_aqi_service),
) -> AQIHistoryResponse:
    hours = _parse_range_hours(range)
    location = location_service.get_location(current_user.id, location_id) if location_id else location_service.get_primary_location(current_user.id)

    if location:
        history = aqi_service.get_history_by_city(city=location.city, hours=hours)
        points = [AQIHistoryPoint(**item) for item in history]
        return AQIHistoryResponse(location_id=location.id, range=f"{hours}h", points=points)

    points = [AQIHistoryPoint(**item) for item in aqi_service.get_history_by_city(city="Delhi", hours=hours)]
    return AQIHistoryResponse(location_id=None, range=f"{hours}h", points=points)
