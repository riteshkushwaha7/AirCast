from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdateRequest


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_or_create(self, firebase_uid: str, email: str | None = None) -> User:
        user = self.user_repository.get_by_firebase_uid(firebase_uid)
        if user:
            return user
        return self.user_repository.create(firebase_uid=firebase_uid, email=email)

    def update_me(self, user: User, payload: UserUpdateRequest) -> User:
        updates = payload.model_dump(exclude_none=True)
        if not updates:
            return user
        return self.user_repository.update(user, updates)

    def complete_onboarding(self, user: User) -> User:
        return self.user_repository.update(user, {"onboarding_completed": True})
