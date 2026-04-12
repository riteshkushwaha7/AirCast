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
from app.services.best_window_service import BestWindowService
from app.services.dataset_service import DatasetService
from app.services.forecast_service import ForecastService
from app.services.feature_service import FeatureService
from app.services.ingestion_service import IngestionService
from app.services.location_service import LocationService
from app.services.notification_service import NotificationService
from app.services.planner_summary_service import PlannerSummaryService
from app.services.preprocessing_service import PreprocessingService
from app.services.profile_service import ProfileService
from app.services.recommendation_service import RecommendationService
from app.services.user_service import UserService
from app.services.weekly_planner_service import WeeklyPlannerService


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(session))


def get_profile_service(session: Session = Depends(get_db_session)) -> ProfileService:
    return ProfileService(ProfileRepository(session))


def get_location_service(session: Session = Depends(get_db_session)) -> LocationService:
    return LocationService(LocationRepository(session))


def get_alert_service(session: Session = Depends(get_db_session)) -> AlertService:
    return AlertService(AlertRepository(session))


def get_forecast_service(
    session: Session = Depends(get_db_session),
    influx_provider: InfluxProvider = Depends(get_influx_provider),
) -> ForecastService:
    timeseries_repo = AQITimeSeriesRepository(influx_provider)
    return ForecastService(ForecastRepository(session), timeseries_repository=timeseries_repo)


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


def get_ingestion_service(
    influx_provider: InfluxProvider = Depends(get_influx_provider),
) -> IngestionService:
    timeseries_repo = AQITimeSeriesRepository(influx_provider)
    return IngestionService(timeseries_repo)


def get_feature_service() -> FeatureService:
    return FeatureService()


def get_preprocessing_service(
    influx_provider: InfluxProvider = Depends(get_influx_provider),
    feature_service: FeatureService = Depends(get_feature_service),
) -> PreprocessingService:
    timeseries_repo = AQITimeSeriesRepository(influx_provider)
    return PreprocessingService(timeseries_repo, feature_service=feature_service)


def get_dataset_service(
    influx_provider: InfluxProvider = Depends(get_influx_provider),
) -> DatasetService:
    timeseries_repo = AQITimeSeriesRepository(influx_provider)
    return DatasetService(timeseries_repo)


def get_assistant_service() -> AssistantService:
    return AssistantService()


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()


def get_weekly_planner_service(
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> WeeklyPlannerService:
    return WeeklyPlannerService(
        forecast_service=forecast_service,
        best_window_service=BestWindowService(),
        summary_service=PlannerSummaryService(),
    )


def get_current_db_user(
    auth_user: AuthenticatedUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> User:
    return user_service.get_or_create(firebase_uid=auth_user.firebase_uid, email=auth_user.email)
