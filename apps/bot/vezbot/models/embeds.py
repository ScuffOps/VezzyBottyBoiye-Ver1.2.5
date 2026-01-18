"""Embed template models."""

from typing import Any

from sqlalchemy import BigInteger, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from vezbot.models.base import Base, TimestampMixin


class EmbedTemplate(Base, TimestampMixin):
    """Saved embed template."""

    __tablename__ = "embed_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    embed_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # Discord embed structure
    components_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )  # Buttons/selects
    webhook_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    def __repr__(self) -> str:
        return f"<EmbedTemplate(id={self.id}, name={self.name})>"
