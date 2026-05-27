from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.payment_attempts.models import PaymentAttempt


class PaymentAttemptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payment_attempt: PaymentAttempt) -> PaymentAttempt:
        self.db.add(payment_attempt)
        self.db.flush()
        self.db.refresh(payment_attempt)
        return payment_attempt

    def get_by_id(self, payment_attempt_id: str) -> PaymentAttempt | None:
        stmt = select(PaymentAttempt).where(
            PaymentAttempt.id == payment_attempt_id
        )
        return self.db.scalar(stmt)

    def get_by_checkout_session_id(
        self,
        checkout_session_id: str,
    ) -> PaymentAttempt | None:
        stmt = select(PaymentAttempt).where(
            PaymentAttempt.checkout_session_id == checkout_session_id
        )
        return self.db.scalar(stmt)

    def get_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> PaymentAttempt | None:
        stmt = select(PaymentAttempt).where(
            PaymentAttempt.provider_payment_id == provider_payment_id
        )
        return self.db.scalar(stmt)

    def list_by_invoice_id(self, invoice_id: str) -> list[PaymentAttempt]:
        stmt = (
            select(PaymentAttempt)
            .where(PaymentAttempt.invoice_id == invoice_id)
            .order_by(PaymentAttempt.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())