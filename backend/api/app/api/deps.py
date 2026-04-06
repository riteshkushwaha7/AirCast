from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, get_current_user
from app.db.influx import InfluxProvider, get_influx_provider
from app.db.postgres import get_db_session
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.forecast_repository import ForecastRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.services.alert_service import AlertService
from app.services.aqi_service import AQIService
from app.services.assistant_service import AssistantService
from app.services.forecast_service import ForecastService
from app.services.location_service import LocationService
from app.services.notification_service import NotificationService
from app.services.profile_service import ProfileService
from app.services.user_service import UserService


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(session))


def get_profile_service(session: Session = Depends(get_db_session)) -> ProfileService:
    return ProfileService(ProfileRepository(session))


def get_location_service(session: Session = Depends(get_db_session)) -> LocationService:
    return LocationService(LocationRepository(session))


def get_alert_service(session: Session = Depends(get_db_session)) -> AlertService:
    return AlertService(AlertRepository(session))


def get_forecast_service(session: Session = Depends(get_db_session)) -> ForecastService:
    return ForecastService(ForecastRepository(session))


def get_notification_service(session: Session = Depends(get_db_session)) -> NotificationService:
    return NotificationService(
        device_repository=DeviceRepository(session),
        notification_repository=NotificationRepository(session),
    )


def get_aqi_service(
    influx_provider: InfluxProvider = Depends(get_influx_provider),
) -> AQIService:
    timeseries_repo = AQITimeSeriesRepository(influx_provider)
    return AQIService(timeseries_repo)


def get_assistant_service() -> AssistantService:
    return AssistantService()


def get_current_db_user(
    auth_user: AuthenticatedUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> User:
    return user_service.get_or_create(firebase_uid=auth_user.firebase_uid, email=auth_user.email)
