from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert_preference import AlertPreference


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user_id(self, user_id) -> AlertPreference | None:
        stmt = select(AlertPreference).where(AlertPreference.user_id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def save(self, preference: AlertPreference) -> AlertPreference:
        self.session.add(preference)
        self.session.commit()
        self.session.refresh(preference)
        return preference
