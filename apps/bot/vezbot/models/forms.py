"""Form template and submission models."""

from typing import Any

from sqlalchemy import BigInteger, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vezbot.models.base import Base, TimestampMixin


class FormTemplate(Base, TimestampMixin):
    """Form template definition."""

    __tablename__ = "form_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    fields_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False
    )  # Array of field definitions

    # Relationships
    submissions: Mapped[list["FormSubmission"]] = relationship(
        "FormSubmission", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FormTemplate(id={self.id}, name={self.name})>"


class FormSubmission(Base, TimestampMixin):
    """Form submission data."""

    __tablename__ = "form_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    form_template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("form_templates.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ticket_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tickets.id"), nullable=True
    )
    data_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, approved, denied
    reviewer_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    template: Mapped["FormTemplate"] = relationship("FormTemplate", back_populates="submissions")

    def __repr__(self) -> str:
        return f"<FormSubmission(id={self.id}, status={self.status})>"
