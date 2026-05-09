from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.integrations.firebase_auth import FirebaseTokenClaims, verify_firebase_token

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    firebase_uid: str
    email: str | None = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    settings = get_settings()

    if credentials is None:
        if settings.allow_mock_auth:
            return AuthenticatedUser(firebase_uid="demo-firebase-uid", email="demo@airwise.app")
        raise UnauthorizedException("Authorization token is required")

    token = credentials.credentials
    claims: FirebaseTokenClaims = verify_firebase_token(token)
    return AuthenticatedUser(firebase_uid=claims.uid, email=claims.email)
