import uuid

from app.modules.providers.schemas import (
    CreateProviderCheckoutRequest,
    CreateProviderCheckoutResponse,
)


class FakePaymentProvider:
    provider_name = "fake_provider"

    def create_checkout_session(
        self,
        request: CreateProviderCheckoutRequest,
    ) -> CreateProviderCheckoutResponse:
        provider_checkout_session_id = f"cs_test_{uuid.uuid4().hex}"

        provider_payment_url = (
            "https://fake-provider.local/checkout/"
            f"{provider_checkout_session_id}"
            f"?invoice_id={request.metadata.invoice_id}"
            f"&checkout_session_id={request.metadata.checkout_session_id}"
            f"&payment_attempt_id={request.metadata.payment_attempt_id}"
        )

        return CreateProviderCheckoutResponse(
            provider_checkout_session_id=provider_checkout_session_id,
            provider_payment_url=provider_payment_url,
        )