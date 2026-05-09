from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorPayload(BaseModel):
    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class APIFailure(BaseModel):
    success: bool = False
    error: ErrorPayload


class MessageResponse(BaseModel):
    message: str


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime
