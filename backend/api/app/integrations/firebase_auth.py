from dataclasses import dataclass

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException


@dataclass
class FirebaseTokenClaims:
    uid: str
    email: str | None = None


def verify_firebase_token(token: str) -> FirebaseTokenClaims:
    """Wrapper stub for Firebase token verification.

    In production, replace this with firebase_admin.auth.verify_id_token.
    """
    settings = get_settings()

    if settings.allow_mock_auth and token.startswith("dev-"):
        return FirebaseTokenClaims(uid="demo-firebase-uid", email="demo@airwise.app")

    if settings.allow_mock_auth and token == "mock-token":
        return FirebaseTokenClaims(uid="demo-firebase-uid", email="demo@airwise.app")

    raise UnauthorizedException("Invalid Firebase token")
