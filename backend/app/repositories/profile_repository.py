from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import UserProfile
from app.utils.enums import HealthProfile, SensitivityLevel


class ProfileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user_id(self, user_id) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_default(self, user_id) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            health_profile=HealthProfile.GENERAL,
            sensitivity_level=SensitivityLevel.NORMAL,
            preferred_activity_types=[],
            display_preferences={"aqi_scale": "standard"},
        )
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def save(self, profile: UserProfile) -> UserProfile:
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile
