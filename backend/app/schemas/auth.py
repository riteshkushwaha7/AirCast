from pydantic import BaseModel, Field


class AuthVerifyRequest(BaseModel):
    firebase_token: str = Field(min_length=10)


class AuthVerifyResponse(BaseModel):
    valid: bool
    firebase_uid: str
    email: str | None = None
