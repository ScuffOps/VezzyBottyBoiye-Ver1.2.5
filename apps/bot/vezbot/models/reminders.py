"""Reminder models."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from vezbot.models.base import Base, TimestampMixin


class Reminder(Base, TimestampMixin):
    """User or channel reminder."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # If channel reminder
    message: Mapped[str] = mapped_column(Text, nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recurring_pattern: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # daily, weekly, monthly
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, remind_at={self.remind_at})>"
