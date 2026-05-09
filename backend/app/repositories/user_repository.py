from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, firebase_uid: str, email: str | None = None, full_name: str | None = None) -> User:
        user = User(firebase_uid=firebase_uid, email=email, full_name=full_name)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User, updates: dict[str, Any]) -> User:
        for key, value in updates.items():
            setattr(user, key, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
