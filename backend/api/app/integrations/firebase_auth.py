import firebase_admin
from firebase_admin import auth
from dataclasses import dataclass

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException


@dataclass
class FirebaseTokenClaims:
    uid: str
    email: str | None = None


def verify_firebase_token(token: str) -> FirebaseTokenClaims:
    settings = get_settings()

    if settings.allow_mock_auth and token.startswith("dev-"):
        return FirebaseTokenClaims(uid="demo-firebase-uid", email="demo@airwise.app")

    if settings.allow_mock_auth and token == "mock-token":
        return FirebaseTokenClaims(uid="demo-firebase-uid", email="demo@airwise.app")

    try:
        decoded_token = auth.verify_id_token(token)
        return FirebaseTokenClaims(
            uid=decoded_token["uid"],
            email=decoded_token.get("email"),
        )
    except Exception as e:
        raise UnauthorizedException(f"Invalid Firebase token: {str(e)}")
