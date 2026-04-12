from fastapi import APIRouter, Depends

from app.api.deps import (
    get_alert_service,
    get_aqi_service,
    get_current_db_user,
    get_forecast_service,
    get_location_service,
    get_notification_service,
    get_profile_service,
    get_recommendation_service,
)
from app.models.user import User
from app.schemas.alert import (
    AlertDecisionRead,
    AlertEvaluateRequest,
    AlertEvaluateResponse,
    AlertPreferenceRead,
    AlertPreferenceUpdateRequest,
    AlertTestSendRequest,
)
from app.services.alert_service import AlertService
from app.services.aqi_service import AQIService
from app.services.forecast_service import ForecastService
from app.services.location_service import LocationService
from app.services.notification_service import NotificationService
from app.services.profile_service import ProfileService
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/preferences", response_model=AlertPreferenceRead)
def get_alert_preferences(
    current_user: User = Depends(get_current_db_user),
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertPreferenceRead:
    preference = alert_service.get_or_create_preferences(current_user.id)
    return AlertPreferenceRead.model_validate(preference)


@router.put("/preferences", response_model=AlertPreferenceRead)
def update_alert_preferences(
    payload: AlertPreferenceUpdateRequest,
    current_user: User = Depends(get_current_db_user),
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertPreferenceRead:
    preference = alert_service.update_preferences(current_user.id, payload)
    return AlertPreferenceRead.model_validate(preference)


@router.post("/evaluate", response_model=AlertEvaluateResponse)
def evaluate_alerts(
    payload: AlertEvaluateRequest,
    current_user: User = Depends(get_current_db_user),
    alert_service: AlertService = Depends(get_alert_service),
    location_service: LocationService = Depends(get_location_service),
    profile_service: ProfileService = Depends(get_profile_service),
    aqi_service: AQIService = Depends(get_aqi_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    notification_service: NotificationService = Depends(get_notification_service),
) -> AlertEvaluateResponse:
    preference = alert_service.get_or_create_preferences(current_user.id)
    profile = profile_service.get_or_create(current_user.id)
    location = (
        location_service.get_location(current_user.id, payload.location_id)
        if payload.location_id
        else location_service.get_primary_location(current_user.id)
    )

    if location:
        reading = aqi_service.get_current_by_city(city=location.city, state=location.state, country=location.country)
        resolved_location_id = location.id
    else:
        reading = aqi_service.get_current_fallback()
        resolved_location_id = None

    forecast_horizons = forecast_service.generate_current_summary(
        user_id=current_user.id,
        location_id=resolved_location_id,
        city=location.city if location else None,
    )
    best_window = forecast_service.best_window()
    recommendation = recommendation_service.build_recommendation(
        current_aqi=float(reading["aqi"]),
        category=reading["category"],
        health_profile=profile.health_profile,
        sensitivity_level=profile.sensitivity_level,
        activity_type=payload.activity_type,
        forecast_horizons=forecast_horizons,
        best_window=best_window,
    )
    recent_logs = notification_service.list_recent_logs(current_user.id, limit=80)
    decisions = alert_service.evaluate_alerts(
        preference=preference,
        current_aqi=float(reading["aqi"]),
        current_category=reading["category"],
        forecast_horizons=forecast_horizons,
        recommendation=recommendation,
        last_notification_logs=recent_logs,
        best_window=best_window,
        now=payload.now,
    )

    return AlertEvaluateResponse(decisions=[AlertDecisionRead.model_validate(decision.__dict__) for decision in decisions])


@router.post("/test-send")
def test_send_alerts(
    payload: AlertTestSendRequest,
    current_user: User = Depends(get_current_db_user),
    alert_service: AlertService = Depends(get_alert_service),
    location_service: LocationService = Depends(get_location_service),
    profile_service: ProfileService = Depends(get_profile_service),
    aqi_service: AQIService = Depends(get_aqi_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    notification_service: NotificationService = Depends(get_notification_service),
) -> dict:
    evaluate_response = evaluate_alerts(
        payload=AlertEvaluateRequest(
            location_id=payload.location_id,
            activity_type=payload.activity_type,
            now=payload.now,
        ),
        current_user=current_user,
        alert_service=alert_service,
        location_service=location_service,
        profile_service=profile_service,
        aqi_service=aqi_service,
        forecast_service=forecast_service,
        recommendation_service=recommendation_service,
        notification_service=notification_service,
    )

    dispatches = []
    for decision in evaluate_response.decisions:
        if not decision.should_send:
            continue
        dispatch = notification_service.send_to_user(
            user_id=current_user.id,
            notification_type=decision.alert_type,
            title=decision.title,
            body=decision.body,
            payload_json=decision.payload,
        )
        dispatches.append(dispatch.model_dump(mode="json"))

    return {
        "evaluated": len(evaluate_response.decisions),
        "sent": len(dispatches),
        "dispatches": dispatches,
    }
