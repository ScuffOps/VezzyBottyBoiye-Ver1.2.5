"""Integration configuration models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from vezbot.models.base import Base, TimestampMixin


class IntegrationConfig(Base, TimestampMixin):
    """Integration configuration per guild."""

    __tablename__ = "integration_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # twitch, youtube, twitter, etc.
    config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<IntegrationConfig(guild_id={self.guild_id}, provider={self.provider})>"
