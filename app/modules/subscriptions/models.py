import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SubscriptionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Subscription(Base):
    __tablename__ = "subscriptions"

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

    plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("plans.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
        index=True,
    )

    current_period_start: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    current_period_end: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
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

    invoices = relationship(
        "Invoice",
        back_populates="subscription",
    )