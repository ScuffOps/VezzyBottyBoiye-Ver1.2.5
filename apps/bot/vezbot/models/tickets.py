"""Ticket models."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vezbot.models.base import Base, TimestampMixin


class Ticket(Base, TimestampMixin):
    """Ticket (thread-based)."""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Thread ID
    thread_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    creator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    form_template_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("form_templates.id"), nullable=True
    )
    state: Mapped[str] = mapped_column(
        String(50), default="open"
    )  # open, pending, closed, archived
    claimed_by_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    form_template: Mapped["FormTemplate | None"] = relationship(
        "FormTemplate", foreign_keys=[form_template_id]
    )
    transcripts: Mapped[list["TicketTranscript"]] = relationship(
        "TicketTranscript", back_populates="ticket", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ticket(id={self.id}, guild_id={self.guild_id}, state={self.state})>"


class TicketTranscript(Base, TimestampMixin):
    """Ticket transcript (markdown + HTML)."""

    __tablename__ = "ticket_transcripts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="transcripts")

    def __repr__(self) -> str:
        return f"<TicketTranscript(id={self.id}, ticket_id={self.ticket_id})>"
