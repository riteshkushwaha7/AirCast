from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_db_user,
    get_location_service,
    get_profile_service,
    get_weekly_planner_service,
)
from app.models.user import User
from app.schemas.planner import (
    PlannerActivityResponse,
    PlannerBestDaysResponse,
    PlannerGenerateDemoRequest,
    PlannerGenerateDemoResponse,
    WeeklyPlannerResponse,
)
from app.services.location_service import LocationService
from app.services.profile_service import ProfileService
from app.services.weekly_planner_service import WeeklyPlannerService
from app.utils.enums import ActivityType

router = APIRouter(prefix="/planner", tags=["planner"])


def _resolve_location(current_user: User, location_id: UUID | None, location_service: LocationService):
    if location_id is None:
        return location_service.get_primary_location(current_user.id)
    return location_service.get_location(current_user.id, location_id)


@router.get("/weekly", response_model=WeeklyPlannerResponse)
def get_weekly_plan(
    location_id: UUID | None = Query(default=None),
    activities: list[ActivityType] | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    profile_service: ProfileService = Depends(get_profile_service),
    weekly_planner_service: WeeklyPlannerService = Depends(get_weekly_planner_service),
) -> WeeklyPlannerResponse:
    profile = profile_service.get_or_create(current_user.id)
    location = _resolve_location(current_user, location_id, location_service)
    activity_preferences = (
        activities
        if activities is not None
        else weekly_planner_service.coerce_activity_types(profile.preferred_activity_types)
    )
    return weekly_planner_service.get_weekly_plan(
        location=location,
        health_profile=profile.health_profile,
        sensitivity_level=profile.sensitivity_level,
        activities=activity_preferences,
    )


@router.get("/best-days", response_model=PlannerBestDaysResponse)
def get_best_days(
    location_id: UUID | None = Query(default=None),
    activities: list[ActivityType] | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    profile_service: ProfileService = Depends(get_profile_service),
    weekly_planner_service: WeeklyPlannerService = Depends(get_weekly_planner_service),
) -> PlannerBestDaysResponse:
    profile = profile_service.get_or_create(current_user.id)
    location = _resolve_location(current_user, location_id, location_service)
    activity_preferences = (
        activities
        if activities is not None
        else weekly_planner_service.coerce_activity_types(profile.preferred_activity_types)
    )
    return weekly_planner_service.get_best_days(
        location=location,
        health_profile=profile.health_profile,
        sensitivity_level=profile.sensitivity_level,
        activities=activity_preferences,
    )


@router.get("/activity", response_model=PlannerActivityResponse)
def get_activity_outlook(
    activity_type: ActivityType = Query(...),
    location_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    profile_service: ProfileService = Depends(get_profile_service),
    weekly_planner_service: WeeklyPlannerService = Depends(get_weekly_planner_service),
) -> PlannerActivityResponse:
    profile = profile_service.get_or_create(current_user.id)
    location = _resolve_location(current_user, location_id, location_service)
    return weekly_planner_service.get_activity_outlook(
        location=location,
        health_profile=profile.health_profile,
        sensitivity_level=profile.sensitivity_level,
        activity_type=activity_type,
    )


@router.post("/generate-demo", response_model=PlannerGenerateDemoResponse)
def generate_demo_week(
    payload: PlannerGenerateDemoRequest,
    current_user: User = Depends(get_current_db_user),
    profile_service: ProfileService = Depends(get_profile_service),
    weekly_planner_service: WeeklyPlannerService = Depends(get_weekly_planner_service),
) -> PlannerGenerateDemoResponse:
    profile = profile_service.get_or_create(current_user.id)
    plan = weekly_planner_service.generate_demo(
        scenario=payload.scenario,
        health_profile=profile.health_profile,
        sensitivity_level=profile.sensitivity_level,
        activities=weekly_planner_service.coerce_activity_types(profile.preferred_activity_types),
    )
    return PlannerGenerateDemoResponse(scenario=payload.scenario, planner=plan)
