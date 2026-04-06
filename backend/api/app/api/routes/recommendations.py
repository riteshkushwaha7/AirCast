from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_aqi_service,
    get_current_db_user,
    get_location_service,
    get_profile_service,
)
from app.models.user import User
from app.schemas.forecast import RecommendationResponse
from app.services.aqi_service import AQIService
from app.services.location_service import LocationService
from app.services.profile_service import ProfileService
from app.services.recommendation_service import RecommendationService
from app.utils.enums import ActivityType

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/current", response_model=RecommendationResponse)
def get_current_recommendation(
    location_id: UUID | None = Query(default=None),
    activity_type: ActivityType | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    profile_service: ProfileService = Depends(get_profile_service),
    aqi_service: AQIService = Depends(get_aqi_service),
) -> RecommendationResponse:
    profile = profile_service.get_or_create(current_user.id)
    location = location_service.get_location(current_user.id, location_id) if location_id else location_service.get_primary_location(current_user.id)

    if location:
        reading = aqi_service.get_current_by_city(city=location.city, state=location.state, country=location.country)
        resolved_location_id = location.id
    else:
        reading = aqi_service.get_current_fallback()
        resolved_location_id = None

    recommendation = RecommendationService().recommend(
        category=reading["category"],
        health_profile=profile.health_profile,
        sensitivity_level=profile.sensitivity_level,
        activity_type=activity_type,
    )

    return RecommendationResponse(
        location_id=resolved_location_id,
        activity_type=activity_type,
        current_aqi=reading["aqi"],
        category=reading["category"],
        **recommendation,
    )
