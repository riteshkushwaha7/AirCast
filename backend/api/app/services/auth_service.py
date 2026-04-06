from datetime import UTC, datetime

from app.integrations.firebase_auth import FirebaseTokenClaims, verify_firebase_token
from app.schemas.auth import AuthVerifyResponse


class AuthService:
    def verify(self, firebase_token: str) -> AuthVerifyResponse:
        claims: FirebaseTokenClaims = verify_firebase_token(firebase_token)
        return AuthVerifyResponse(valid=True, firebase_uid=claims.uid, email=claims.email)

    def now(self) -> datetime:
        return datetime.now(tz=UTC)
