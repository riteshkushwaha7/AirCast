from fastapi import APIRouter, Depends

from app.api.deps import get_current_db_user, get_profile_service
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpdateRequest
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileRead)
def get_profile(
    current_user: User = Depends(get_current_db_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    profile = profile_service.get_or_create(current_user.id)
    return ProfileRead.model_validate(profile)


@router.put("", response_model=ProfileRead)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_db_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    profile = profile_service.update(current_user.id, payload)
    return ProfileRead.model_validate(profile)
