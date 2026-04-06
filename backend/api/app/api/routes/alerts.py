from fastapi import APIRouter, Depends

from app.api.deps import get_alert_service, get_current_db_user
from app.models.user import User
from app.schemas.alert import AlertPreferenceRead, AlertPreferenceUpdateRequest
from app.services.alert_service import AlertService

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
