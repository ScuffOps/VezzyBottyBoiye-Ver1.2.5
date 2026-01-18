"""User profile models."""

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from vezbot.models.base import Base, TimestampMixin


class UserProfile(Base, TimestampMixin):
    """User profile with timezone and currency."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)  # IANA timezone
    currency_balance: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("user_id", "guild_id", name="uq_user_guild"),)

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, guild_id={self.guild_id})>"
