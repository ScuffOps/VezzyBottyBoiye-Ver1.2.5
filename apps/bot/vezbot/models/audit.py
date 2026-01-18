"""Audit and error log models."""

from typing import Any

from sqlalchemy import BigInteger, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from vezbot.models.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """Audit log for actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ticket, poll, config, etc.
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action})>"


class ErrorLog(Base, TimestampMixin):
    """Error log with correlation IDs."""

    __tablename__ = "error_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False)  # UUID
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<ErrorLog(id={self.id}, error_type={self.error_type})>"
