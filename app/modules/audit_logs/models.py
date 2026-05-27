import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, Enum, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEntityType(StrEnum):
    ACCOUNT = "ACCOUNT"
    PLAN = "PLAN"
    SUBSCRIPTION = "SUBSCRIPTION"
    INVOICE = "INVOICE"
    CHECKOUT_SESSION = "CHECKOUT_SESSION"
    PAYMENT_ATTEMPT = "PAYMENT_ATTEMPT"
    PAYMENT_EVENT = "PAYMENT_EVENT"


class AuditAction(StrEnum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    STATE_CHANGED = "STATE_CHANGED"
    PROVIDER_CHECKOUT_CREATED = "PROVIDER_CHECKOUT_CREATED"
    PROVIDER_CHECKOUT_FAILED = "PROVIDER_CHECKOUT_FAILED"
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"
    WEBHOOK_PROCESSED = "WEBHOOK_PROCESSED"
    WEBHOOK_IGNORED = "WEBHOOK_IGNORED"
    WEBHOOK_FAILED = "WEBHOOK_FAILED"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    entity_type: Mapped[AuditEntityType] = mapped_column(
        Enum(AuditEntityType),
        nullable=False,
        index=True,
    )

    entity_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction),
        nullable=False,
        index=True,
    )

    before_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    after_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )