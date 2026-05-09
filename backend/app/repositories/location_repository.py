from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.location import SavedLocation


class LocationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_user(self, user_id) -> list[SavedLocation]:
        stmt = select(SavedLocation).where(SavedLocation.user_id == user_id).order_by(SavedLocation.created_at.desc())
        return list(self.session.execute(stmt).scalars())

    def get_for_user(self, user_id, location_id) -> SavedLocation | None:
        stmt = select(SavedLocation).where(and_(SavedLocation.user_id == user_id, SavedLocation.id == location_id))
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, location: SavedLocation) -> SavedLocation:
        self.session.add(location)
        self.session.commit()
        self.session.refresh(location)
        return location

    def save(self, location: SavedLocation) -> SavedLocation:
        self.session.add(location)
        self.session.commit()
        self.session.refresh(location)
        return location

    def delete(self, location: SavedLocation) -> None:
        self.session.delete(location)
        self.session.commit()

    def unset_primary_for_user(self, user_id) -> None:
        rows = self.list_by_user(user_id)
        for row in rows:
            if row.is_primary:
                row.is_primary = False
                self.session.add(row)
        self.session.commit()
