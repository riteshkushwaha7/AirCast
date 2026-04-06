from sqlalchemy.orm import Session

from app.models.location import SavedLocation
from app.models.profile import UserProfile
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.services.mock_data import SAMPLE_LOCATIONS, SAMPLE_PROFILE, SAMPLE_USER


def seed_demo(session: Session) -> User:
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)
    location_repo = LocationRepository(session)
    alert_repo = AlertRepository(session)

    user = user_repo.get_by_firebase_uid(SAMPLE_USER["firebase_uid"])
    if not user:
        user = user_repo.create(
            firebase_uid=SAMPLE_USER["firebase_uid"],
            email=SAMPLE_USER["email"],
            full_name=SAMPLE_USER["full_name"],
        )

    profile = profile_repo.get_by_user_id(user.id)
    if not profile:
        profile = UserProfile(
            user_id=user.id,
            health_profile=SAMPLE_PROFILE["health_profile"],
            sensitivity_level=SAMPLE_PROFILE["sensitivity_level"],
            preferred_activity_types=[item.value for item in SAMPLE_PROFILE["preferred_activity_types"]],
            display_preferences=SAMPLE_PROFILE["display_preferences"],
        )
        profile_repo.save(profile)

    existing_locations = location_repo.list_by_user(user.id)
    if not existing_locations:
        for item in SAMPLE_LOCATIONS:
            location_repo.create(
                SavedLocation(
                    user_id=user.id,
                    label=item["label"],
                    city=item["city"],
                    state=item["state"],
                    country=item["country"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    source_type=item["source_type"],
                    is_primary=item["is_primary"],
                )
            )

    preference = alert_repo.get_by_user_id(user.id)
    if not preference:
        from app.models.alert_preference import AlertPreference

        alert_repo.save(AlertPreference(user_id=user.id))

    return user
