from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.modules.payment_events.models import PaymentEventStatus


class PaymentEventResponse(BaseModel):
    id: str
    provider_name: str
    provider_event_id: str
    event_type: str
    payload: dict[str, Any]
    status: PaymentEventStatus
    received_at: datetime
    processed_at: datetime | None
    error_message: str | None

    model_config = {
        "from_attributes": True,
    }