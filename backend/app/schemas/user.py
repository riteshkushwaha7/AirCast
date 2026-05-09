from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    firebase_uid: str
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class UserOnboardingCompleteResponse(BaseModel):
    onboarding_completed: bool
    completed_at: datetime
