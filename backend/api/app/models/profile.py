import uuid

from sqlalchemy import JSON, ForeignKey, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.utils.enums import ActivityType, HealthProfile, SensitivityLevel


class UserProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    health_profile: Mapped[HealthProfile] = mapped_column(
        SQLEnum(HealthProfile, name="health_profile_enum", native_enum=False),
        default=HealthProfile.GENERAL,
        nullable=False,
    )
    sensitivity_level: Mapped[SensitivityLevel] = mapped_column(
        SQLEnum(SensitivityLevel, name="sensitivity_level_enum", native_enum=False),
        default=SensitivityLevel.NORMAL,
        nullable=False,
    )
    preferred_activity_types: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    display_preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="profile")

    __table_args__ = (Index("ix_user_profiles_user_id", "user_id"),)
