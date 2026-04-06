from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import LocationSourceType


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    label: str
    city: str
    state: str | None = None
    country: str
    latitude: float
    longitude: float
    source_type: LocationSourceType
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class LocationCreateRequest(BaseModel):
    label: str = Field(min_length=1, max_length=64)
    city: str = Field(min_length=1, max_length=96)
    state: str | None = Field(default=None, max_length=96)
    country: str = Field(default="India", min_length=1, max_length=96)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    source_type: LocationSourceType = LocationSourceType.MANUAL
    is_primary: bool = False


class LocationUpdateRequest(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=64)
    city: str | None = Field(default=None, min_length=1, max_length=96)
    state: str | None = Field(default=None, max_length=96)
    country: str | None = Field(default=None, min_length=1, max_length=96)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    source_type: LocationSourceType | None = None


class SetPrimaryLocationResponse(BaseModel):
    location_id: UUID
    is_primary: bool = True
