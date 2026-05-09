from app.core.exceptions import NotFoundException
from app.models.location import SavedLocation
from app.repositories.location_repository import LocationRepository
from app.schemas.location import LocationCreateRequest, LocationUpdateRequest
from app.utils.validators import validate_latitude, validate_longitude


class LocationService:
    def __init__(self, location_repository: LocationRepository) -> None:
        self.location_repository = location_repository

    def list_locations(self, user_id) -> list[SavedLocation]:
        return self.location_repository.list_by_user(user_id)

    def get_location(self, user_id, location_id) -> SavedLocation:
        location = self.location_repository.get_for_user(user_id, location_id)
        if not location:
            raise NotFoundException("Location not found")
        return location

    def create_location(self, user_id, payload: LocationCreateRequest) -> SavedLocation:
        validate_latitude(payload.latitude)
        validate_longitude(payload.longitude)

        if payload.is_primary:
            self.location_repository.unset_primary_for_user(user_id)

        location = SavedLocation(
            user_id=user_id,
            label=payload.label,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            latitude=payload.latitude,
            longitude=payload.longitude,
            source_type=payload.source_type,
            is_primary=payload.is_primary,
        )
        return self.location_repository.create(location)

    def update_location(self, user_id, location_id, payload: LocationUpdateRequest) -> SavedLocation:
        location = self.get_location(user_id, location_id)

        updates = payload.model_dump(exclude_none=True)
        if "latitude" in updates:
            validate_latitude(float(updates["latitude"]))
        if "longitude" in updates:
            validate_longitude(float(updates["longitude"]))

        for key, value in updates.items():
            setattr(location, key, value)

        return self.location_repository.save(location)

    def delete_location(self, user_id, location_id) -> None:
        location = self.get_location(user_id, location_id)
        self.location_repository.delete(location)

    def set_primary(self, user_id, location_id) -> SavedLocation:
        location = self.get_location(user_id, location_id)

        self.location_repository.unset_primary_for_user(user_id)
        location.is_primary = True
        return self.location_repository.save(location)

    def get_primary_location(self, user_id) -> SavedLocation | None:
        locations = self.location_repository.list_by_user(user_id)
        for location in locations:
            if location.is_primary:
                return location
        return locations[0] if locations else None
