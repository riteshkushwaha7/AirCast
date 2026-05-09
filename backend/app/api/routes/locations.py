from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_current_db_user, get_location_service
from app.models.user import User
from app.schemas.location import LocationCreateRequest, LocationRead, LocationUpdateRequest, SetPrimaryLocationResponse
from app.services.location_service import LocationService

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationRead])
def list_locations(
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
) -> list[LocationRead]:
    locations = location_service.list_locations(current_user.id)
    return [LocationRead.model_validate(item) for item in locations]


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreateRequest,
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
) -> LocationRead:
    location = location_service.create_location(current_user.id, payload)
    return LocationRead.model_validate(location)


@router.patch("/{location_id}", response_model=LocationRead)
def update_location(
    location_id: UUID,
    payload: LocationUpdateRequest,
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
) -> LocationRead:
    location = location_service.update_location(current_user.id, location_id, payload)
    return LocationRead.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: UUID,
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
) -> Response:
    location_service.delete_location(current_user.id, location_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{location_id}/set-primary", response_model=SetPrimaryLocationResponse)
def set_primary_location(
    location_id: UUID,
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
) -> SetPrimaryLocationResponse:
    location = location_service.set_primary(current_user.id, location_id)
    return SetPrimaryLocationResponse(location_id=location.id, is_primary=location.is_primary)
