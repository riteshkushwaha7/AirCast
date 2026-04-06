from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken
from app.utils.time import utcnow


class DeviceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, token: DeviceToken) -> DeviceToken:
        existing = self.get_by_fcm_token(token.fcm_token)
        if existing:
            existing.platform = token.platform
            existing.device_name = token.device_name
            existing.user_id = token.user_id
            existing.is_active = True
            existing.last_seen_at = utcnow()
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing

        self.session.add(token)
        self.session.commit()
        self.session.refresh(token)
        return token

    def get_by_fcm_token(self, fcm_token: str) -> DeviceToken | None:
        stmt = select(DeviceToken).where(DeviceToken.fcm_token == fcm_token)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_for_user(self, user_id, token_id) -> DeviceToken | None:
        stmt = select(DeviceToken).where(and_(DeviceToken.user_id == user_id, DeviceToken.id == token_id))
        return self.session.execute(stmt).scalar_one_or_none()

    def list_active_for_user(self, user_id) -> list[DeviceToken]:
        stmt = select(DeviceToken).where(and_(DeviceToken.user_id == user_id, DeviceToken.is_active.is_(True)))
        return list(self.session.execute(stmt).scalars())

    def deactivate(self, token: DeviceToken) -> DeviceToken:
        token.is_active = False
        self.session.add(token)
        self.session.commit()
        self.session.refresh(token)
        return token
