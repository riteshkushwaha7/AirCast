from app.schemas.alert import AlertPreferenceRead, AlertPreferenceUpdateRequest
from app.schemas.assistant import AssistantExplainRequest, AssistantExplainResponse
from app.schemas.auth import AuthVerifyRequest, AuthVerifyResponse
from app.schemas.common import APIResponse, APIFailure, MessageResponse
from app.schemas.forecast import (
    AQICurrentResponse,
    AQIHistoryResponse,
    BestWindowResponse,
    ForecastCurrentResponse,
    ForecastGenerateDemoResponse,
    RecommendationResponse,
    WeeklyForecastResponse,
)
from app.schemas.location import LocationCreateRequest, LocationRead, LocationUpdateRequest
from app.schemas.notification import DeviceTokenRegisterRequest
from app.schemas.profile import ProfileRead, ProfileUpdateRequest
from app.schemas.user import UserRead, UserUpdateRequest

__all__ = [
    "APIResponse",
    "APIFailure",
    "MessageResponse",
    "UserRead",
    "UserUpdateRequest",
    "ProfileRead",
    "ProfileUpdateRequest",
    "LocationRead",
    "LocationCreateRequest",
    "LocationUpdateRequest",
    "AlertPreferenceRead",
    "AlertPreferenceUpdateRequest",
    "DeviceTokenRegisterRequest",
    "AQICurrentResponse",
    "AQIHistoryResponse",
    "ForecastCurrentResponse",
    "WeeklyForecastResponse",
    "BestWindowResponse",
    "ForecastGenerateDemoResponse",
    "RecommendationResponse",
    "AssistantExplainRequest",
    "AssistantExplainResponse",
    "AuthVerifyRequest",
    "AuthVerifyResponse",
]
