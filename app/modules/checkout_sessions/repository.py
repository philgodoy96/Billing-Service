from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.checkout_sessions.models import (
    CheckoutSession,
    CheckoutSessionStatus,
)


ACTIVE_CHECKOUT_STATUSES = {
    CheckoutSessionStatus.PENDING_PROVIDER,
    CheckoutSessionStatus.CREATED,
}


class CheckoutSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, checkout_session: CheckoutSession) -> CheckoutSession:
        self.db.add(checkout_session)
        self.db.flush()
        self.db.refresh(checkout_session)
        return checkout_session

    def get_by_id(self, checkout_session_id: str) -> CheckoutSession | None:
        stmt = select(CheckoutSession).where(
            CheckoutSession.id == checkout_session_id
        )
        return self.db.scalar(stmt)

    def get_by_provider_checkout_session_id(
        self,
        provider_checkout_session_id: str,
    ) -> CheckoutSession | None:
        stmt = select(CheckoutSession).where(
            CheckoutSession.provider_checkout_session_id
            == provider_checkout_session_id
        )
        return self.db.scalar(stmt)

    def get_active_by_invoice_id(
        self,
        invoice_id: str,
    ) -> CheckoutSession | None:
        stmt = (
            select(CheckoutSession)
            .where(CheckoutSession.invoice_id == invoice_id)
            .where(CheckoutSession.status.in_(ACTIVE_CHECKOUT_STATUSES))
            .order_by(CheckoutSession.created_at.desc())
        )
        return self.db.scalar(stmt)

    def list_by_invoice_id(self, invoice_id: str) -> list[CheckoutSession]:
        stmt = (
            select(CheckoutSession)
            .where(CheckoutSession.invoice_id == invoice_id)
            .order_by(CheckoutSession.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())