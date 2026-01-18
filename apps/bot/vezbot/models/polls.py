"""Poll models."""

from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, BigInteger, Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vezbot.models.base import Base, TimestampMixin


class Poll(Base, TimestampMixin):
    """Poll definition."""

    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    creator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    options_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False
    )  # Array of {label, emoji, index}
    type: Mapped[str] = mapped_column(String(50), default="single")  # single, multi
    closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    votes: Mapped[list["PollVote"]] = relationship(
        "PollVote", back_populates="poll", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Poll(id={self.id}, question={self.question[:50]})>"


class PollVote(Base, TimestampMixin):
    """Poll vote record."""

    __tablename__ = "poll_votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    poll_id: Mapped[int] = mapped_column(Integer, ForeignKey("polls.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    option_indices: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)

    # Relationships
    poll: Mapped["Poll"] = relationship("Poll", back_populates="votes")

    __table_args__ = ({"sqlite_autoincrement": True},)

    def __repr__(self) -> str:
        return f"<PollVote(poll_id={self.poll_id}, user_id={self.user_id})>"
