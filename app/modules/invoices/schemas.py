from datetime import datetime

from pydantic import BaseModel

from app.modules.invoices.models import InvoiceStatus


class InvoiceResponse(BaseModel):
    id: str
    account_id: str
    subscription_id: str
    status: InvoiceStatus
    amount_cents: int
    currency: str
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: datetime
    paid_at: datetime | None
    voided_at: datetime | None
    provider_invoice_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }