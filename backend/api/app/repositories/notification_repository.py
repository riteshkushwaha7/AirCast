from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification_log import NotificationLog


class NotificationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, log: NotificationLog) -> NotificationLog:
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_for_user(self, user_id, limit: int = 50) -> list[NotificationLog]:
        stmt = (
            select(NotificationLog)
            .where(NotificationLog.user_id == user_id)
            .order_by(NotificationLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars())

    def list_recent_by_types(self, user_id, notification_types: list, limit: int = 100) -> list[NotificationLog]:
        stmt = (
            select(NotificationLog)
            .where(NotificationLog.user_id == user_id)
            .where(NotificationLog.notification_type.in_(notification_types))
            .order_by(NotificationLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars())
