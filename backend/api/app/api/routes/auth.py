from fastapi import APIRouter

from app.schemas.auth import AuthVerifyRequest, AuthVerifyResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/verify", response_model=AuthVerifyResponse)
def verify_token(payload: AuthVerifyRequest) -> AuthVerifyResponse:
    service = AuthService()
    return service.verify(payload.firebase_token)
