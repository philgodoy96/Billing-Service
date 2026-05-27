from datetime import datetime

from pydantic import BaseModel

from app.modules.payment_attempts.models import PaymentAttemptStatus


class PaymentAttemptResponse(BaseModel):
    id: str
    invoice_id: str
    checkout_session_id: str
    provider_payment_id: str | None
    status: PaymentAttemptStatus
    amount_cents: int
    currency: str
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }