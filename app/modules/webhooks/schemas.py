from typing import Any

from pydantic import BaseModel, Field


class FakeProviderWebhookMetadata(BaseModel):
    account_id: str | None = None
    subscription_id: str | None = None
    invoice_id: str | None = None
    checkout_session_id: str | None = None
    payment_attempt_id: str | None = None


class FakeProviderWebhookPayload(BaseModel):
    provider_event_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    provider_checkout_session_id: str | None = None
    provider_payment_id: str | None = None
    failure_reason: str | None = None
    metadata: FakeProviderWebhookMetadata = Field(
        default_factory=FakeProviderWebhookMetadata
    )
    data: dict[str, Any] = Field(default_factory=dict)


class WebhookIngestionResponse(BaseModel):
    received: bool