from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.payment_attempts.models import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from app.modules.payment_attempts.repository import PaymentAttemptRepository
from app.modules.payment_attempts.state_machine import (
    ensure_payment_attempt_can_be_cancelled,
    ensure_payment_attempt_can_fail,
    ensure_payment_attempt_can_succeed,
)


class PaymentAttemptService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.payment_attempts = PaymentAttemptRepository(db)

    def create_pending_attempt(
        self,
        *,
        invoice_id: str,
        checkout_session_id: str,
        amount_cents: int,
        currency: str,
    ) -> PaymentAttempt:
        payment_attempt = PaymentAttempt(
            invoice_id=invoice_id,
            checkout_session_id=checkout_session_id,
            status=PaymentAttemptStatus.PENDING,
            amount_cents=amount_cents,
            currency=currency,
        )

        return self.payment_attempts.create(payment_attempt)

    def get_payment_attempt(self, payment_attempt_id: str) -> PaymentAttempt:
        payment_attempt = self.payment_attempts.get_by_id(payment_attempt_id)

        if payment_attempt is None:
            raise NotFoundError("Payment attempt not found.")

        return payment_attempt

    def get_by_checkout_session_id(
        self,
        checkout_session_id: str,
    ) -> PaymentAttempt:
        payment_attempt = self.payment_attempts.get_by_checkout_session_id(
            checkout_session_id
        )

        if payment_attempt is None:
            raise NotFoundError("Payment attempt not found for checkout session.")

        return payment_attempt

    def mark_succeeded(
        self,
        payment_attempt: PaymentAttempt,
        *,
        provider_payment_id: str,
    ) -> PaymentAttempt:
        ensure_payment_attempt_can_succeed(payment_attempt.status)

        if payment_attempt.status == PaymentAttemptStatus.SUCCEEDED:
            return payment_attempt

        payment_attempt.status = PaymentAttemptStatus.SUCCEEDED
        payment_attempt.provider_payment_id = provider_payment_id
        payment_attempt.failure_reason = None

        self.db.flush()
        self.db.refresh(payment_attempt)

        return payment_attempt

    def mark_failed(
        self,
        payment_attempt: PaymentAttempt,
        *,
        provider_payment_id: str | None = None,
        failure_reason: str | None = None,
    ) -> PaymentAttempt:
        ensure_payment_attempt_can_fail(payment_attempt.status)

        if payment_attempt.status == PaymentAttemptStatus.FAILED:
            return payment_attempt

        payment_attempt.status = PaymentAttemptStatus.FAILED
        payment_attempt.provider_payment_id = provider_payment_id
        payment_attempt.failure_reason = failure_reason

        self.db.flush()
        self.db.refresh(payment_attempt)

        return payment_attempt

    def mark_cancelled(
        self,
        payment_attempt: PaymentAttempt,
        *,
        reason: str | None = None,
    ) -> PaymentAttempt:
        ensure_payment_attempt_can_be_cancelled(payment_attempt.status)

        if payment_attempt.status == PaymentAttemptStatus.CANCELLED:
            return payment_attempt

        payment_attempt.status = PaymentAttemptStatus.CANCELLED
        payment_attempt.failure_reason = reason

        self.db.flush()
        self.db.refresh(payment_attempt)

        return payment_attempt