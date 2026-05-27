import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvoiceStatus(StrEnum):
    OPEN = "OPEN"
    PAID = "PAID"
    FAILED = "FAILED"
    VOID = "VOID"
    EXPIRED = "EXPIRED"


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )

    subscription_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("subscriptions.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus),
        nullable=False,
        default=InvoiceStatus.OPEN,
        index=True,
    )

    amount_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    billing_period_start: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    billing_period_end: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    voided_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    provider_invoice_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    subscription = relationship(
        "Subscription",
        back_populates="invoices",
    )