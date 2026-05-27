from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.modules.checkout_sessions.models import (
    CheckoutSession,
    CheckoutSessionStatus,
)
from app.modules.checkout_sessions.repository import CheckoutSessionRepository
from app.modules.checkout_sessions.schemas import CheckoutSessionCreate
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.invoices.service import InvoiceService
from app.modules.payment_attempts.models import PaymentAttempt
from app.modules.payment_attempts.service import PaymentAttemptService
from app.modules.providers.fake_provider import FakePaymentProvider
from app.modules.providers.schemas import (
    CreateProviderCheckoutRequest,
    ProviderCheckoutMetadata,
)


class CheckoutSessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.checkout_sessions = CheckoutSessionRepository(db)
        self.invoices = InvoiceService(db)
        self.payment_attempts = PaymentAttemptService(db)
        self.provider = FakePaymentProvider()

    def create_checkout_session(
        self,
        data: CheckoutSessionCreate,
    ) -> tuple[CheckoutSession, PaymentAttempt]:
        invoice = self.invoices.get_invoice(data.invoice_id)
        self._ensure_invoice_is_payable(invoice)

        existing_checkout_session = (
            self.checkout_sessions.get_active_by_invoice_id(invoice.id)
        )

        if existing_checkout_session is not None:
            existing_payment_attempt = (
                self.payment_attempts.get_by_checkout_session_id(
                    existing_checkout_session.id
                )
            )
            return existing_checkout_session, existing_payment_attempt

        try:
            checkout_session = CheckoutSession(
                invoice_id=invoice.id,
                status=CheckoutSessionStatus.PENDING_PROVIDER,
                provider_name=self.provider.provider_name,
                provider_checkout_session_id=None,
                provider_payment_url=None,
                idempotency_key="temporary",
                expires_at=None,
            )

            created_checkout_session = self.checkout_sessions.create(
                checkout_session
            )

            created_checkout_session.idempotency_key = (
                f"checkout_session_{created_checkout_session.id}"
            )

            payment_attempt = self.payment_attempts.create_pending_attempt(
                invoice_id=invoice.id,
                checkout_session_id=created_checkout_session.id,
                amount_cents=invoice.amount_cents,
                currency=invoice.currency,
            )

            self._create_provider_checkout_session(
                checkout_session=created_checkout_session,
                payment_attempt=payment_attempt,
                invoice=invoice,
            )

            self.db.commit()

            self.db.refresh(created_checkout_session)
            self.db.refresh(payment_attempt)

            return created_checkout_session, payment_attempt

        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Checkout session conflict.") from exc
        except Exception:
            self.db.rollback()
            raise

    def get_checkout_session(
        self,
        checkout_session_id: str,
    ) -> CheckoutSession:
        checkout_session = self.checkout_sessions.get_by_id(checkout_session_id)

        if checkout_session is None:
            raise NotFoundError("Checkout session not found.")

        return checkout_session

    def get_by_provider_checkout_session_id(
        self,
        provider_checkout_session_id: str,
    ) -> CheckoutSession:
        checkout_session = (
            self.checkout_sessions.get_by_provider_checkout_session_id(
                provider_checkout_session_id
            )
        )

        if checkout_session is None:
            raise NotFoundError("Checkout session not found for provider id.")

        return checkout_session

    def mark_completed(
        self,
        checkout_session: CheckoutSession,
    ) -> CheckoutSession:
        if checkout_session.status == CheckoutSessionStatus.COMPLETED:
            return checkout_session

        if checkout_session.status in {
            CheckoutSessionStatus.FAILED,
            CheckoutSessionStatus.EXPIRED,
            CheckoutSessionStatus.CANCELLED,
        }:
            raise ValidationError(
                f"Checkout session with status {checkout_session.status} cannot complete."
            )

        checkout_session.status = CheckoutSessionStatus.COMPLETED
        checkout_session.provider_error_message = None

        self.db.flush()
        self.db.refresh(checkout_session)

        return checkout_session

    def mark_failed(
        self,
        checkout_session: CheckoutSession,
        *,
        error_message: str,
    ) -> CheckoutSession:
        if checkout_session.status == CheckoutSessionStatus.COMPLETED:
            raise ValidationError("A completed checkout session cannot be failed.")

        checkout_session.status = CheckoutSessionStatus.FAILED
        checkout_session.provider_error_message = error_message

        self.db.flush()
        self.db.refresh(checkout_session)

        return checkout_session

    def mark_expired(
        self,
        checkout_session: CheckoutSession,
    ) -> CheckoutSession:
        if checkout_session.status == CheckoutSessionStatus.COMPLETED:
            raise ValidationError("A completed checkout session cannot expire.")

        if checkout_session.status == CheckoutSessionStatus.EXPIRED:
            return checkout_session

        checkout_session.status = CheckoutSessionStatus.EXPIRED

        self.db.flush()
        self.db.refresh(checkout_session)

        return checkout_session

    def _create_provider_checkout_session(
        self,
        *,
        checkout_session: CheckoutSession,
        payment_attempt: PaymentAttempt,
        invoice: Invoice,
    ) -> None:
        checkout_session.provider_creation_attempt_count += 1
        checkout_session.last_provider_attempt_at = datetime.utcnow()

        provider_request = CreateProviderCheckoutRequest(
            amount_cents=invoice.amount_cents,
            currency=invoice.currency,
            idempotency_key=checkout_session.idempotency_key,
            metadata=ProviderCheckoutMetadata(
                account_id=invoice.account_id,
                subscription_id=invoice.subscription_id,
                invoice_id=invoice.id,
                checkout_session_id=checkout_session.id,
                payment_attempt_id=payment_attempt.id,
            ),
        )

        provider_response = self.provider.create_checkout_session(
            provider_request
        )

        checkout_session.provider_checkout_session_id = (
            provider_response.provider_checkout_session_id
        )
        checkout_session.provider_payment_url = (
            provider_response.provider_payment_url
        )
        checkout_session.status = CheckoutSessionStatus.CREATED
        checkout_session.expires_at = datetime.utcnow() + timedelta(hours=24)
        checkout_session.provider_error_message = None

        self.db.flush()
        self.db.refresh(checkout_session)

    def _ensure_invoice_is_payable(self, invoice: Invoice) -> None:
        if invoice.status != InvoiceStatus.OPEN:
            raise ValidationError(
                f"Only OPEN invoices can create checkout sessions. Current status: {invoice.status}."
            )