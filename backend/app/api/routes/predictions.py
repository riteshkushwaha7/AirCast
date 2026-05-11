from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_db_user, get_location_service, get_prediction_service
from app.models.user import User
from app.schemas.prediction import PredictionRunRequest, PredictionRunResponse
from app.services.location_service import LocationService
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/run", response_model=PredictionRunResponse)
def run_prediction(
    payload: PredictionRunRequest,
    current_user: User = Depends(get_current_db_user),
    location_service: LocationService = Depends(get_location_service),
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> PredictionRunResponse:
    location = location_service.get_location(current_user.id, payload.location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    try:
        result = prediction_service.run(
            city=location.city,
            location_id=str(payload.location_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": str(exc)},
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(exc)},
        ) from exc

    return PredictionRunResponse(**result)
