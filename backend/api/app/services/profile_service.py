from app.models.profile import UserProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileUpdateRequest


class ProfileService:
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self.profile_repository = profile_repository

    def get_or_create(self, user_id) -> UserProfile:
        profile = self.profile_repository.get_by_user_id(user_id)
        if profile:
            return profile
        return self.profile_repository.create_default(user_id)

    def update(self, user_id, payload: ProfileUpdateRequest) -> UserProfile:
        profile = self.get_or_create(user_id)
        profile.health_profile = payload.health_profile
        profile.sensitivity_level = payload.sensitivity_level
        profile.preferred_activity_types = [item.value for item in payload.preferred_activity_types]
        profile.display_preferences = payload.display_preferences
        return self.profile_repository.save(profile)
