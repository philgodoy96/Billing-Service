from datetime import datetime

from pydantic import BaseModel

from app.modules.checkout_sessions.models import CheckoutSessionStatus
from app.modules.payment_attempts.schemas import PaymentAttemptResponse


class CheckoutSessionCreate(BaseModel):
    invoice_id: str


class CheckoutSessionResponse(BaseModel):
    id: str
    invoice_id: str
    status: CheckoutSessionStatus
    provider_name: str
    provider_checkout_session_id: str | None
    provider_payment_url: str | None
    idempotency_key: str
    provider_error_message: str | None
    provider_creation_attempt_count: int
    last_provider_attempt_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class CreateCheckoutSessionResponse(BaseModel):
    checkout_session: CheckoutSessionResponse
    payment_attempt: PaymentAttemptResponse

    model_config = {
        "from_attributes": True,
    }