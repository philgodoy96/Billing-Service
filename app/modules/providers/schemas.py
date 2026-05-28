from pydantic import BaseModel, Field


class ProviderCheckoutMetadata(BaseModel):
    account_id: str
    subscription_id: str
    invoice_id: str
    checkout_session_id: str
    payment_attempt_id: str


class CreateProviderCheckoutRequest(BaseModel):
    amount_cents: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: str = Field(min_length=1, max_length=255)
    metadata: ProviderCheckoutMetadata


class CreateProviderCheckoutResponse(BaseModel):
    provider_checkout_session_id: str
    provider_payment_url: str