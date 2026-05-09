from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.api.deps import get_current_db_user, get_user_service
from app.models.user import User
from app.schemas.user import UserOnboardingCompleteResponse, UserRead, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_db_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_db_user),
    user_service: UserService = Depends(get_user_service),
) -> UserRead:
    updated = user_service.update_me(current_user, payload)
    return UserRead.model_validate(updated)


@router.post("/onboarding/complete", response_model=UserOnboardingCompleteResponse)
def complete_onboarding(
    current_user: User = Depends(get_current_db_user),
    user_service: UserService = Depends(get_user_service),
) -> UserOnboardingCompleteResponse:
    user_service.complete_onboarding(current_user)
    return UserOnboardingCompleteResponse(onboarding_completed=True, completed_at=datetime.now(tz=UTC))
